from __future__ import annotations

from typing import Sequence

from .base import Action, SimpleAction
from ..events import Message


class StartRoom:
    name = "Start Room"

    def __init__(self) -> None:
        self._cleared = False

    def get_actions(self) -> Sequence[Action]:
        return [SimpleAction(key="proceed", description="Proceed to the next room")]

    def resolve_action(self, action_key: str, state) -> None:
        if action_key == "proceed":
            state.bus.publish(Message(text="You proceed to the next room."))
            self._cleared = True

    def is_cleared(self) -> bool:
        return self._cleared
