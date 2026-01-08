from __future__ import annotations

from typing import Sequence

from .base import Action, SimpleAction
from ..events import GameWon, Message


class ExitRoom:
    name = "Exit Room"

    def __init__(self) -> None:
        self._cleared = False

    def get_actions(self) -> Sequence[Action]:
        return [SimpleAction(key="exit", description="Exit the dungeon")]

    def resolve_action(self, action_key: str, state) -> None:
        if action_key == "exit":
            state.bus.publish(Message(text="You exit the dungeon victorious!"))
            state.won = True
            state.bus.publish(GameWon())
            self._cleared = True

    def is_cleared(self) -> bool:
        return self._cleared
