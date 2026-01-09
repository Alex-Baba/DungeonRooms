from __future__ import annotations

from src.events import EventBus
from src.events.types import Message


def test_event_bus_dispatches_to_subscribers() -> None:
    bus = EventBus()
    received: list[str] = []

    def on_message(event: Message) -> None:
        received.append(event.text)

    bus.subscribe(Message, on_message)
    bus.publish(Message(text="hello"))

    assert received == ["hello"]


def test_event_bus_does_not_dispatch_other_event_types() -> None:
    bus = EventBus()
    received: list[str] = []

    def on_message(event: Message) -> None:
        received.append(event.text)

    bus.subscribe(Message, on_message)

    class Other:
        def __init__(self, text: str) -> None:
            self.text = text

    bus.publish(Other(text="nope"))

    assert received == []
