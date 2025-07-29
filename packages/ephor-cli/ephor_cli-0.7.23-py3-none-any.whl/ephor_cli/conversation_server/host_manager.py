import json
import uuid
from typing import Any, Callable

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.messages.base import message_to_dict

from ephor_cli.conversation_server.host_agent import HostAgent
from ephor_cli.services import (
    agent_service,
    message_service,
)
from ephor_cli.utils.chunk_streamer import ChunkStreamer
from ephor_cli.utils.sanitize_message import sanitize_message
from ephor_cli.types.sse import SSEEvent


class ADKHostManager:
    """An implementation of memory based management with fake agent actions

    This implements the interface of the ApplicationManager to plug into
    the AgentServer. This acts as the service contract that the Mesop app
    uses to send messages to the agent and provide information for the frontend.
    """

    def __init__(
        self,
        user_id: str,
        project_id: str,
        conversation_id: str,
        context: str,
        enqueue_event_for_sse: Callable[[Any], None],
    ):
        self.user_id = user_id
        self.project_id = project_id
        self.conversation_id = conversation_id
        self.context = context
        self.enqueue_event_for_sse = enqueue_event_for_sse
        self.chunk_streamer = ChunkStreamer()
        self.host_agent = self._create_host_agent()

    def _create_host_agent(self) -> HostAgent:
        """Get or create a host agent for a specific conversation."""
        agents = agent_service.list_agents(
            self.user_id, self.project_id, self.conversation_id
        )
        messages = message_service.list_messages(
            self.user_id, self.project_id, self.conversation_id
        )

        messages = sanitize_message(messages)

        return HostAgent(
            conversation_id=self.conversation_id,
            project_id=self.project_id,
            user_id=self.user_id,
            remote_agent_addresses=[agent.url for agent in agents],
            initial_state=messages,
            enqueue_event_for_sse=self.enqueue_event_for_sse,
            context=self.context,
        )

    def sanitize_message(self, message: BaseMessage) -> BaseMessage:
        messages = message_service.list_messages(
            self.user_id, self.project_id, self.conversation_id
        )
        if messages:
            message.additional_kwargs.update({"last_message_id": messages[-1].id})
        return message

    def _add_new_messages(self, message: BaseMessage, new_messages: list[BaseMessage]):
        last_message_id = message.id
        for new_message in new_messages:
            new_message.id = str(uuid.uuid4())
            new_message.additional_kwargs.update({"last_message_id": last_message_id})
            if isinstance(new_message, AIMessage):
                new_message.additional_kwargs["agent"] = "host_agent"
            message_service.add_message(
                self.user_id, self.project_id, self.conversation_id, new_message
            )
            last_message_id = new_message.id

    async def cancel(self, message_id: str = None):
        """Cancel current message processing and all active remote agent tasks."""
        print(f"[HostManager] Cancelling message {message_id}")
        await self.host_agent.cancel_all_tasks()
        self.chunk_streamer.cancel()
        
    def _should_use_direct_routing(self, message: BaseMessage) -> tuple[bool, str | None]:
        """Check if we should use direct routing based on target_agent_names.
        
        Returns:
            tuple: (should_route_directly, target_agent_name_or_none)
        """
        target_agent_names = message.additional_kwargs.get("target_agent_names", [])
        
        # Only route directly if there's exactly one agent specified
        if isinstance(target_agent_names, list) and len(target_agent_names) == 1:
            target_agent_name = target_agent_names[0]
            
            # Check if the agent exists in our registered agents
            available_agents = {agent["name"] for agent in self.host_agent._list_remote_agents()}
            
            if target_agent_name in available_agents:
                print(f"[HostManager] Direct routing to agent: {target_agent_name}")
                return True, target_agent_name
            else:
                print(f"[HostManager] Target agent '{target_agent_name}' not found. Available: {available_agents}")
        
        return False, None

    async def _process_direct_routing(self, message: BaseMessage, target_agent_name: str):
        """Process message with direct routing to a specific agent."""
        print(f"[HostManager] Processing direct routing to {target_agent_name}")
        
        # Extract the original user message content
        original_message_content = self._extract_clean_message_content(message)
        
        # Create a message that instructs the moderator to send the original content directly
        directed_content = f"Send the following message exactly as written to {target_agent_name} : {original_message_content}"
        
        clean_message = HumanMessage(
            content=directed_content,
            additional_kwargs=message.additional_kwargs.copy()
        )
        clean_message.id = message.id
        
        # Use the normal flow but with the direct instruction
        await self._process_normal_flow(clean_message)

    def _extract_clean_message_content(self, message: BaseMessage) -> str:
        if isinstance(message.content, str):
            return message.content
        elif isinstance(message.content, list):
            # Extract only text parts, ignore images and large data
            text_parts = []
            for part in message.content:
                if part.get("type") == "text":
                    text_parts.append(part.get("text", ""))
            return " ".join(text_parts) if text_parts else str(message.content)
        else:
            return str(message.content)

    async def _process_normal_flow(self, message: BaseMessage):
        """Process message through normal moderator flow."""
        print("[HostManager] Processing through normal moderator flow")

        self.chunk_streamer.reset()
        async for chunk in self.chunk_streamer.process(
            self.host_agent.astream(message)
        ):
            sse_event = SSEEvent(
                actor="host_agent",
                content=json.dumps(message_to_dict(chunk)),
            )
            if self.enqueue_event_for_sse:
                await self.enqueue_event_for_sse(sse_event)
                print("[HostManager] Successfully put event in the queue")

        messages = self.chunk_streamer.messages
        self._add_new_messages(message, messages)

    async def process_message(self, message: BaseMessage):
        """Process a message, either through direct routing or normal flow."""
        
        # Check if we should use direct routing
        should_route_directly, target_agent_name = self._should_use_direct_routing(message)
        
        if should_route_directly and target_agent_name is not None:
            await self._process_direct_routing(message, target_agent_name)
        else:
            await self._process_normal_flow(message)

