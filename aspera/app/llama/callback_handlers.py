import json
import logging
import asyncio

from typing import Optional, Dict, List, Any, AsyncGenerator

from pydantic import BaseModel
from anyio.streams.memory import MemoryObjectSendStream
from llama_index.core.callbacks.base import BaseCallbackHandler
from llama_index.core.callbacks.schema import CBEventType, EventPayload
from llama_index.core.tools.types import ToolOutput

from app.schemas.chat import StreamedEvent


logger = logging.getLogger(__name__)


class CallbackEvent(BaseModel):
    event_type: CBEventType
    payload: Optional[Dict[str, Any]] = None
    event_id: str = ""

    def get_retrieval_message(self) -> dict | None:
        if self.payload is None:
            return None

        nodes = self.payload.get("nodes")
        if nodes:
            msg = f"Retrieved {len(nodes)} sources to use as context for the query"
        else:
            msg = f"Retrieving context for query: '{self.payload.get('query_str')}'"
        return {
            "type": "events",
            "data": {"title": msg}
        }

    def get_tool_message(self) -> dict | None:
        if self.payload is None:
            return None
        func_call_args = self.payload.get("function_call")
        if func_call_args is not None and "tool" in self.payload:
            tool = self.payload.get("tool")
            if tool is None:
                return None
            return {
                "type": "events",
                "data": {
                    "title": f"Calling tool: {tool.name} with inputs: {func_call_args}",
                },
            }
        return None

    def _is_output_serializable(self, output: Any) -> bool:
        try:
            json.dumps(output)
            return True
        except TypeError:
            return False

    def get_agent_tool_response(self) -> dict | None:
        if self.payload is None:
            return None
        response = self.payload.get("response")
        if response is not None:
            sources = response.sources
            for source in sources:
                # Return the tool response here to include the toolCall information
                if isinstance(source, ToolOutput):
                    if self._is_output_serializable(source.raw_output):
                        output = source.raw_output
                    else:
                        output = source.content

                    return {
                        "type": "tools",
                        "data": {
                            "toolOutput": {
                                "output": output,
                                "isError": source.is_error,
                            },
                            "toolCall": {
                                "id": None,  # There is no tool id in the ToolOutput
                                "name": source.tool_name,
                                "input": source.raw_input,
                            },
                        },
                    }
        return None

    def to_response(self):
        try:
            match self.event_type:
                case "retrieve":
                    return self.get_retrieval_message()
                case "function_call":
                    return self.get_tool_message()
                case "agent_step":
                    return self.get_agent_tool_response()
                case _:
                    return None
        except Exception as e:
            logger.error(f"Error in converting event to response: {e}")
            return None


class ChatCallbackHandler(BaseCallbackHandler):

    is_done: bool = False

    def __init__(self, send_stream: MemoryObjectSendStream):
        ignored_events = [
            CBEventType.CHUNKING,
            CBEventType.NODE_PARSING,
            CBEventType.EMBEDDING,
            CBEventType.LLM,
            CBEventType.TEMPLATING
        ]
        super().__init__(ignored_events, ignored_events)
        self._send_stream = send_stream
        
    def on_event_start(
            self,
            event_type: CBEventType,
            payload: Optional[Dict[str, Any]] = None,
            event_id: str = "",
            parent_id: str = "",
            **kwargs: Any
    ) -> str:
        event = CallbackEvent(event_id=event_id, event_type=event_type, payload=payload)
        if event.to_response() is not None:
            asyncio.create_task(self.async_on_event(event))
        return event_id

    def on_event_end(
            self,
            event_type: CBEventType,
            payload: Optional[Dict[str, Any]] = None,
            event_id: str = "",
            **kwargs: Any
    ) -> None:
        event = CallbackEvent(event_id=event_id, event_type=event_type, payload=payload)
        if event.to_response() is not None:
            asyncio.create_task(self.async_on_event(event))

    def start_trace(self, trace_id: Optional[str] = None) -> None:
        """ No-op."""

    def end_trace(self, trace_id: Optional[str] = None, trace_map: Optional[Dict[str, List[str]]] = None) -> None:
        """ No-op."""

    async def async_on_event(self, event: CallbackEvent):
        await self._send_stream.send(StreamedEvent(content=json.dumps(event.to_response())))
