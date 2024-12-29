from collections import defaultdict
from typing import Callable, Dict, List, Any
import asyncio


class EventManager:
    def __init__(self):
        self._handlers: Dict[str, List[Callable[..., Any]]] = defaultdict(list)

    def on(self, event: str, handler: Callable[..., Any]) -> None:
        self._handlers[event].append(handler)

    def off(self, event: str, handler: Callable[..., Any]) -> None:
        if event in self._handlers:
            self._handlers[event].remove(handler)
            if not self._handlers[event]:
                del self._handlers[event]

    def clear(self, event: str = None) -> None:
        if event:
            self._handlers.pop(event, None)
        else:
            self._handlers.clear()

    async def emit(self, event: str, *args: Any, **kwargs: Any) -> None:
        if event not in self._handlers:
            return

        results = []
        for handler in self._handlers[event]:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(*args, **kwargs)
            else:
                if asyncio.get_event_loop().is_running():
                    result = await asyncio.get_event_loop().run_in_executor(
                        None, handler, *args, **dict(kwargs)
                    )
                else:
                    result = handler(*args, **kwargs)
            results.append(result)

        return results if results else None

    def has_listeners(self, event: str) -> bool:
        return bool(self._handlers.get(event))

    def listener_count(self, event: str) -> int:
        return len(self._handlers.get(event, []))
