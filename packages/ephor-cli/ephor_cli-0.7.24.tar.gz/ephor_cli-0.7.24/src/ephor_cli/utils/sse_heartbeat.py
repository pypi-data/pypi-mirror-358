"""
SSE Heartbeat Utility
Provides background heartbeat functionality for Server-Sent Events to prevent connection drops
"""

import asyncio
import time
from typing import Dict, Callable, Any


class SSEHeartbeatManager:
    """Manages background heartbeat tasks for SSE streams"""
    
    def __init__(self):
        self.heartbeat_tasks: Dict[str, asyncio.Task] = {}
    
    async def start_heartbeat(
        self, 
        stream_id: str, 
        enqueue_function: Callable[[str, Any], None],
        interval: float = 1.0
    ):
        """Start background heartbeat for a specific stream"""
        async def heartbeat_loop():
            try:
                while True:
                    # Create heartbeat event
                    heartbeat_event = f'data: {{"type":"heartbeat","timestamp":{time.time()}}}\n\n'
                    
                    # Send heartbeat using the provided enqueue function
                    await enqueue_function(stream_id, heartbeat_event)
                    
                    await asyncio.sleep(interval)
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"[SSEHeartbeat] Error in heartbeat loop for stream {stream_id}: {e}")
        
        # Cancel existing heartbeat if any
        await self.stop_heartbeat(stream_id)
        
        # Start new heartbeat task
        task = asyncio.create_task(heartbeat_loop())
        self.heartbeat_tasks[stream_id] = task
    
    async def stop_heartbeat(self, stream_id: str):
        """Stop heartbeat for a specific stream"""
        if stream_id in self.heartbeat_tasks:
            task = self.heartbeat_tasks[stream_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            del self.heartbeat_tasks[stream_id]
    
    def cleanup_all(self):
        """Cancel all heartbeat tasks"""
        for stream_id in list(self.heartbeat_tasks.keys()):
            task = self.heartbeat_tasks[stream_id]
            task.cancel()
            del self.heartbeat_tasks[stream_id]


# Global instance for shared use
_heartbeat_manager = SSEHeartbeatManager()


def start_sse_heartbeat(
    stream_id: str, 
    enqueue_function: Callable[[str, Any], None],
    interval: float = 1.0
):
    """Start heartbeat for an SSE stream (non-async wrapper)"""
    asyncio.create_task(
        _heartbeat_manager.start_heartbeat(stream_id, enqueue_function, interval)
    )


async def stop_sse_heartbeat(stream_id: str):
    """Stop heartbeat for an SSE stream"""
    await _heartbeat_manager.stop_heartbeat(stream_id)


def is_heartbeat_event(data: str) -> bool:
    """Check if an event is a heartbeat event"""
    return isinstance(data, str) and '"type":"heartbeat"' in data 