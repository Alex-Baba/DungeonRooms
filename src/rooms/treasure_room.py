from __future__ import annotations

from typing import Sequence
import random

from .base import Action, SimpleAction
from ..events import Message


class TreasureRoom:
    name = "Treasure Room"

    def __init__(self, rng: random.Random) -> None:
        self._cleared = False
        self._rng = rng

    def get_actions(self) -> Sequence[Action]:
        return [SimpleAction(key="open_chest", description="Open the treasure chest")]

    def resolve_action(self, action_key: str, state) -> None:
        if action_key == "open_chest" and not self._cleared:
            state.bus.publish(Message(text="You open the chest."))
            items = ["healing_potion", "mystery_potion", "bomb"]
            found_item = self._rng.choice(items)
            state.player.add_item(found_item, source=self.name, event_bus=state.bus)

            gold_amount = self._rng.randint(10, 100)
            state.player.add_gold(gold_amount, source=self.name, event_bus=state.bus)

            self._cleared = True

    def is_cleared(self) -> bool:
        return self._cleared
