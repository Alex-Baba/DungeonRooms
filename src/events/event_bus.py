from __future__ import annotations

from typing import Any, Callable, Dict, List, Type


# Define a type alias for event handler functions
EventHandler = Callable[[Any], None]


class EventBus:
    """A simple event bus for managing event subscriptions and dispatching events."""

    def __init__(self) -> None:
        self._subs: Dict[Type[Any], List[EventHandler]] = {}

    #register event handlers for specific event types
    def subscribe(self, event_type: Type[Any], handler: EventHandler) -> None:
        self._subs.setdefault(event_type, []).append(handler)

    #publish events to all subscribed handlers
    def publish(self, event: Any) -> None:
        for handler in self._subs.get(type(event), []):
            handler(event)
