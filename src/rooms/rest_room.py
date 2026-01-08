from __future__ import annotations

from typing import Sequence
import random

from .base import Action, SimpleAction
from ..events import Message


class RestRoom:
    name = "Rest Room"

    def __init__(self, rng: random.Random) -> None:
        self._cleared = False
        self._rng = rng

    def get_actions(self) -> Sequence[Action]:
        return [SimpleAction(key="rest", description="Rest to recover health")]

    def resolve_action(self, action_key: str, state) -> None:
        if action_key == "rest" and not self._cleared:
            heal_amount = self._rng.randint(10, 30)
            state.player.heal(heal_amount, source=self.name, event_bus=state.bus)
            state.bus.publish(Message(text=f"You rested and recovered {heal_amount} health!"))
            self._cleared = True

    def is_cleared(self) -> bool:
        return self._cleared
