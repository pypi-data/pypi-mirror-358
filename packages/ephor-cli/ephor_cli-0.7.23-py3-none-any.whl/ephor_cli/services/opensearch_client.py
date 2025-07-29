import os
import logging
from typing import List, Dict, Any, Optional
from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy.exceptions import OpenSearchException
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from requests_aws4auth import AWS4Auth
from ephor_cli.constant import AWS_OPENSEARCH_ENDPOINT
from ephor_cli.constant import AWS_OPENSEARCH_INDEX_NAME

logger = logging.getLogger(__name__)

class OpenSearchClient:
    """Client for AWS OpenSearch Service with vector search capabilities."""
    
    def __init__(self):
        self.endpoint = AWS_OPENSEARCH_ENDPOINT
        self.index_name = AWS_OPENSEARCH_INDEX_NAME
        self.region = "us-east-1"  
        
        # Remove https:// if present
        if self.endpoint.startswith('https://'):
            self.endpoint = self.endpoint[8:]
        
        self.client = self._create_client()
        
    def _create_client(self) -> OpenSearch:
        """Create OpenSearch client with AWS authentication."""
        try:
            # Get AWS credentials
            session = boto3.Session()
            credentials = session.get_credentials()
            
            # Create AWS4Auth for authentication
            awsauth = AWS4Auth(
                credentials.access_key,
                credentials.secret_key,
                self.region,
                'es',
                session_token=credentials.token
            )
            
            client = OpenSearch(
                hosts=[{'host': self.endpoint, 'port': 443}],
                http_auth=awsauth,
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection,
                timeout=60
            )
            
            # Test connection
            client.info()
            logger.info(f"Successfully connected to OpenSearch at {self.endpoint}")
            return client
            
        except Exception as e:
            logger.error(f"Failed to create OpenSearch client: {e}")
            raise
    
    def create_vector_index(self) -> bool:
        """Create vector index with proper mapping for embeddings."""
        mapping = {
            "mappings": {
                "properties": {
                    "conversation_id": {"type": "keyword"},
                    "attachment_id": {"type": "keyword"},
                    "space_id": {"type": "keyword"},  # Add space_id to mapping
                    "user_id": {"type": "keyword"},  # Add user_id to mapping - FIXED to keyword
                    "project_id": {"type": "keyword"},  # Add project_id to mapping - FIXED to keyword
                    "scope": {"type": "keyword"},  # Add scope to mapping - FIXED to keyword
                    "filename": {"type": "text"},
                    "chunk_index": {"type": "integer"},
                    "chunk_text": {"type": "text"},
                    "file_type": {"type": "keyword"},
                    "content_type": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "embedding_vector": {
                        "type": "knn_vector",
                        "dimension": 1536,  # OpenAI text-embedding-3-small dimension
                        "method": {
                            "name": "hnsw",
                            "space_type": "cosinesimil",
                            "engine": "lucene"
                        }
                    }
                }
            },
            "settings": {
                "index": {
                    "knn": True,
                    "knn.algo_param.ef_search": 100
                }
            }
        }
        
        try:
            if self.client.indices.exists(index=self.index_name):
                logger.info(f"Index {self.index_name} already exists")
                return True
                
            response = self.client.indices.create(
                index=self.index_name,
                body=mapping
            )
            logger.info(f"Created vector index {self.index_name}: {response}")
            return True
            
        except OpenSearchException as e:
            logger.error(f"Failed to create vector index: {e}")
            return False
    
    def store_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """Store document chunks with embeddings in bulk."""
        try:
            bulk_body = []
            
            for chunk in chunks:
                # Index action
                bulk_body.append({
                    "index": {
                        "_index": self.index_name,
                        "_id": f"{chunk['conversation_id']}_{chunk['attachment_id']}_{chunk['chunk_index']}"
                    }
                })
                # Document data
                bulk_body.append(chunk)
            
            response = self.client.bulk(body=bulk_body)
            
            if response.get('errors'):
                logger.error(f"Bulk indexing errors: {response}")
                return False
                
            logger.info(f"Successfully stored {len(chunks)} chunks")
            return True
            
        except OpenSearchException as e:
            logger.error(f"Failed to store chunks: {e}")
            return False
    
    def similarity_search(self, query_vector: List[float], conversation_id: str, 
                         top_k: int = 5, similarity_threshold: float = 0.7, space_id: str = None) -> List[Dict[str, Any]]:
        """Perform cosine similarity search for relevant chunks."""
        try:
            # Determine filter field and value based on space_id availability
            filter_field = "space_id" if space_id else "conversation_id"
            filter_value = space_id if space_id else conversation_id
            
            # Use proper KNN query structure with integrated filtering
            query_body = {
                "size": top_k * 2,  # Get more results to allow for filtering
                "query": {
                    "knn": {
                        "embedding_vector": {
                            "vector": query_vector,
                            "k": top_k * 2,
                            "filter": {
                                "term": {filter_field: filter_value}
                            }
                        }
                    }
                },
                "_source": [
                    "conversation_id", "attachment_id", "space_id", "filename", 
                    "chunk_index", "chunk_text", "file_type", "content_type", "created_at"
                ]
            }
            
            response = self.client.search(
                index=self.index_name,
                body=query_body
            )
            
            results = []
            for hit in response['hits']['hits']:
                # Results are already filtered by space_id or conversation_id at query level
                    
                # OpenSearch KNN returns scores that need to be converted to similarity
                # For cosine similarity with HNSW, score = 1 / (1 + distance)
                # where distance = 1 - cosine_similarity
                # So: cosine_similarity = 1 - (1/score - 1) = 2 - 1/score
                raw_score = hit['_score']
                
                # Handle edge cases
                if raw_score <= 0:
                    similarity = 0.0
                elif raw_score >= 1.0:
                    # Direct cosine similarity (close to 1.0)
                    similarity = min(raw_score, 1.0)
                else:
                    # Convert HNSW score to cosine similarity
                    # For cosinesimil space_type: similarity = 2 - (1/score)
                    similarity = max(0.0, min(1.0, 2.0 - (1.0 / raw_score)))
                
                if similarity >= similarity_threshold:
                    result = hit['_source']
                    result['similarity_score'] = similarity
                    results.append(result)
            
            # Deduplicate results before limiting to top_k
            deduplicated_results = self._deduplicate_chunks(results)
            
            search_type = "space_id" if space_id else "conversation_id"
            logger.info(f"Found {len(results)} total chunks, {len(deduplicated_results)} after deduplication (filtered by {search_type})")
            return deduplicated_results[:top_k]
            
        except OpenSearchException as e:
            logger.error(f"Similarity search failed: {e}")
            return []
    
    def similarity_search_with_scope(self, query_vector: List[float], conversation_id: str, 
                                     user_id: str, project_id: str, space_id: str = None,
                                     top_k: int = 10, similarity_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Search for similar content across different scopes (global + project + conversation).
        
        Args:
            query_vector: The embedding vector to search with
            conversation_id: Current conversation ID
            user_id: User ID for scope filtering
            project_id: Project ID for scope filtering
            space_id: Space ID for space-scoped attachments
            top_k: Maximum number of results to return
            similarity_threshold: Minimum similarity threshold
            
        Returns:
            List of relevant chunks with similarity scores
        """
        try:
            # Build query for backward compatibility with existing chunks
            should_clauses = [
                # NEW: Scope-based chunks with keyword fields (future data)
                {
                    "bool": {
                        "must": [
                            {"term": {"user_id": user_id}},
                            {"term": {"scope": "global"}}
                        ]
                    }
                },  # Global attachments for this user
                {
                    "bool": {
                        "must": [
                            {"term": {"user_id": user_id}},
                            {"term": {"scope": "project"}},
                            {"term": {"project_id": project_id}}
                        ]
                    }
                },  # Project-level attachments for this project
                # EXISTING: Scope-based chunks with text fields (current data)
                {
                    "bool": {
                        "must": [
                            {"match": {"user_id": user_id}},
                            {"match": {"scope": "global"}}
                        ]
                    }
                },  # Global attachments for this user (text fields)
                {
                    "bool": {
                        "must": [
                            {"match": {"user_id": user_id}},
                            {"match": {"scope": "project"}},
                            {"match": {"project_id": project_id}}
                        ]
                    }
                },  # Project-level attachments for this project (text fields)
                # LEGACY: Backward compatibility - chunks without scope fields
                {"term": {"conversation_id": conversation_id}}  # Current conversation attachments (legacy chunks)
            ]
            
            # Add space-scoped attachments if space_id is provided
            if space_id:
                should_clauses.extend([
                    {
                        "bool": {
                            "must": [
                                {"term": {"user_id": user_id}},
                                {"term": {"scope": "space"}},
                                {"term": {"space_id": space_id}}
                            ]
                        }
                    },  # New space-scoped chunks (keyword fields)
                    {
                        "bool": {
                            "must": [
                                {"match": {"user_id": user_id}},
                                {"match": {"scope": "space"}},
                                {"term": {"space_id": space_id}}
                            ]
                        }
                    },  # Existing space-scoped chunks (text fields)
                    {"term": {"space_id": space_id}}  # Legacy space chunks without scope field
                ])
            
            search_body = {
                "size": top_k * 2,  # Get more results to filter by threshold
                "query": {
                    "knn": {
                        "embedding_vector": {
                            "vector": query_vector,
                            "k": top_k * 2,
                            "filter": {
                                "bool": {
                                    "should": should_clauses,
                                    "minimum_should_match": 1
                                }
                            }
                        }
                    }
                },
                "_source": [
                    "conversation_id", "attachment_id", "space_id", "user_id", "project_id", 
                    "scope", "filename", "chunk_index", "chunk_text", "file_type", 
                    "content_type", "created_at"
                ]
            }
            
            response = self.client.search(
                index=self.index_name,
                body=search_body
            )
            
            # Process results and filter by similarity threshold
            results = []
            for hit in response["hits"]["hits"]:
                # OpenSearch KNN returns scores that need to be converted to similarity
                # For cosine similarity with HNSW, score = 1 / (1 + distance)
                # where distance = 1 - cosine_similarity
                # So: cosine_similarity = 1 - (1/score - 1) = 2 - 1/score
                raw_score = hit.get("_score", 0)
                
                # Handle edge cases
                if raw_score <= 0:
                    similarity = 0.0
                elif raw_score >= 1.0:
                    # Direct cosine similarity (close to 1.0)
                    similarity = min(raw_score, 1.0)
                else:
                    # Convert HNSW score to cosine similarity
                    # For cosinesimil space_type: similarity = 2 - (1/score)
                    similarity = max(0.0, min(1.0, 2.0 - (1.0 / raw_score)))
                
                if similarity >= similarity_threshold:
                    chunk_data = hit["_source"]
                    chunk_data["similarity_score"] = similarity
                    results.append(chunk_data)
            
            # Deduplicate results based on attachment_id + chunk_index + filename
            # Keep the most recent version (latest created_at) of each unique chunk
            deduplicated_results = self._deduplicate_chunks(results)
            
            # Sort by score and limit to top_k
            deduplicated_results.sort(key=lambda x: x["similarity_score"], reverse=True)
            logger.info(f"Found {len(results)} total chunks, {len(deduplicated_results)} after deduplication (user: {user_id}, project: {project_id})")
            return deduplicated_results[:top_k]
            
        except OpenSearchException as e:
            logger.error(f"Failed to perform scope-based similarity search: {e}")
            return []
    
    def _deduplicate_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate chunks based on attachment_id + chunk_index + filename.
        
        Keeps the most recent version (latest created_at) of each unique chunk.
        This solves the issue where the same file has been indexed multiple times.
        
        Args:
            chunks: List of chunk dictionaries from search results
            
        Returns:
            Deduplicated list of chunks
        """
        if not chunks:
            return chunks
            
        # Group chunks by unique identifier (attachment_id + chunk_index + filename)
        chunk_groups = {}
        
        for chunk in chunks:
            # Create unique key for deduplication
            attachment_id = chunk.get('attachment_id', '')
            chunk_index = chunk.get('chunk_index', 0)
            filename = chunk.get('filename', '')
            
            unique_key = f"{attachment_id}_{chunk_index}_{filename}"
            
            if unique_key not in chunk_groups:
                chunk_groups[unique_key] = []
            chunk_groups[unique_key].append(chunk)
        
        # For each group, keep only the most recent chunk (latest created_at)
        deduplicated_chunks = []
        duplicates_removed = 0
        
        for unique_key, group_chunks in chunk_groups.items():
            if len(group_chunks) == 1:
                # No duplicates
                deduplicated_chunks.append(group_chunks[0])
            else:
                # Multiple versions - keep the most recent one
                duplicates_removed += len(group_chunks) - 1
                
                # Sort by created_at descending (most recent first)
                group_chunks.sort(key=lambda x: x.get('created_at', ''), reverse=True)
                most_recent = group_chunks[0]
                
                # Also prioritize higher similarity scores in case of same timestamp
                if len(group_chunks) > 1 and group_chunks[0].get('created_at') == group_chunks[1].get('created_at'):
                    group_chunks.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
                    most_recent = group_chunks[0]
                
                deduplicated_chunks.append(most_recent)
        
        if duplicates_removed > 0:
            logger.info(f"Removed {duplicates_removed} duplicate chunks, kept {len(deduplicated_chunks)} unique chunks")
        
        return deduplicated_chunks
    
    def delete_conversation_chunks(self, conversation_id: str, space_id: str = None) -> bool:
        """Delete all chunks for a conversation or space."""
        try:
            if space_id:
                # Delete all chunks in a space
                query_body = {
                    "query": {
                        "term": {
                            "space_id": space_id
                        }
                    }
                }
            else:
                # Delete chunks for a specific conversation
                query_body = {
                    "query": {
                        "term": {
                            "conversation_id": conversation_id
                        }
                    }
                }
            
            response = self.client.delete_by_query(
                index=self.index_name,
                body=query_body
            )
            
            deleted = response.get('deleted', 0)
            scope = f"space {space_id}" if space_id else f"conversation {conversation_id}"
            logger.info(f"Deleted {deleted} chunks for {scope}")
            return True
            
        except OpenSearchException as e:
            logger.error(f"Failed to delete conversation chunks: {e}")
            return False
    
    def delete_space_chunks(self, space_id: str) -> bool:
        """Delete all chunks for a specific space."""
        return self.delete_conversation_chunks(conversation_id="", space_id=space_id)
    
    def delete_attachment_chunks(self, attachment_id: str) -> bool:
        """Delete all chunks for a specific attachment."""
        try:
            query_body = {
                "query": {
                    "term": {
                        "attachment_id": attachment_id
                    }
                }
            }
            
            response = self.client.delete_by_query(
                index=self.index_name,
                body=query_body
            )
            
            deleted = response.get('deleted', 0)
            logger.info(f"Deleted {deleted} chunks for attachment {attachment_id}")
            return deleted > 0
            
        except OpenSearchException as e:
            logger.error(f"Failed to delete attachment chunks: {e}")
            return False
    
    def delete_specific_chunks(self, conversation_id: str, attachment_id: str) -> bool:
        """Delete chunks for a specific attachment within a conversation."""
        try:
            query_body = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"conversation_id": conversation_id}},
                            {"term": {"attachment_id": attachment_id}}
                        ]
                    }
                }
            }
            
            response = self.client.delete_by_query(
                index=self.index_name,
                body=query_body
            )
            
            deleted = response.get('deleted', 0)
            logger.info(f"Deleted {deleted} chunks for attachment {attachment_id} in conversation {conversation_id}")
            return deleted > 0
            
        except OpenSearchException as e:
            logger.error(f"Failed to delete specific chunks: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Check OpenSearch cluster health."""
        try:
            health = self.client.cluster.health()
            info = self.client.info()
            
            return {
                "status": health.get('status', 'unknown'),
                "cluster_name": health.get('cluster_name', 'unknown'),
                "version": info.get('version', {}).get('number', 'unknown'),
                "connected": True
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "red",
                "connected": False,
                "error": str(e)
            }
    
    def update_attachment_scope(self, attachment_id: str, scope: str, user_id: str, project_id: str) -> bool:
        """Update scope, user_id, and project_id for all chunks of a specific attachment.
        
        Args:
            attachment_id: The ID of the attachment to update
            scope: The new scope value ('space', 'project', or 'global')
            user_id: User ID for the chunks
            project_id: Project ID for the chunks
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update all chunks for this attachment
            update_body = {
                "script": {
                    "source": "ctx._source.scope = params.scope; ctx._source.user_id = params.user_id; ctx._source.project_id = params.project_id",
                    "params": {
                        "scope": scope,
                        "user_id": user_id,
                        "project_id": project_id
                    }
                },
                "query": {
                    "term": {
                        "attachment_id": attachment_id
                    }
                }
            }
            
            response = self.client.update_by_query(
                index=self.index_name,
                body=update_body
            )
            
            updated = response.get('updated', 0)
            logger.info(f"Updated {updated} chunks for attachment {attachment_id} with scope '{scope}'")
            return updated > 0
            
        except OpenSearchException as e:
            logger.error(f"Failed to update attachment scope: {e}")
            return False 