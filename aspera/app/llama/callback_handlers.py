from typing import Optional, Dict, List, Any

from anyio.streams.memory import MemoryObjectSendStream

from llama_index.core.callbacks.base import BaseCallbackHandler
from llama_index.core.callbacks.schema import CBEventType, EventPayload


class ChatCallbackHandler(BaseCallbackHandler):

    def __init__(self, send_stream: MemoryObjectSendStream):
        ignored_events = [CBEventType.CHUNKING, CBEventType.NODE_PARSING]
        super().__init__(ignored_events, ignored_events)
        self.__send_stream = send_stream
        
    def on_event_start(self, event_type: CBEventType, payload: Optional[Dict[str, Any]] = None, event_id: str = "",
                       parent_id: str = "", **kwargs: Any) -> str:
        pass

    def on_event_end(self, event_type: CBEventType, payload: Optional[Dict[str, Any]] = None, event_id: str = "",
                     **kwargs: Any) -> None:
        if event_type == CBEventType.SUB_QUESTION:
            qa_pair = payload[EventPayload.SUB_QUESTION]
            print("Sub Question: " + qa_pair.sub_q.sub_question.strip())
            print("Answer: " + qa_pair.answer.strip())

    def start_trace(self, trace_id: Optional[str] = None) -> None:
        pass

    def end_trace(self, trace_id: Optional[str] = None, trace_map: Optional[Dict[str, List[str]]] = None) -> None:
        pass
