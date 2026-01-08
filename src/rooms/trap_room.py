from __future__ import annotations

from typing import Sequence
import random

from .base import Action, SimpleAction
from ..events import Message


class TrapRoom:
    name = "Trap Room"

    def __init__(self, rng: random.Random) -> None:
        self._cleared = False
        self._rng = rng

    def get_actions(self) -> Sequence[Action]:
        return [
            SimpleAction(key="disarm_trap", description="Attempt to disarm the trap"),
            SimpleAction(key="leave", description="Leave the trap"),
        ]

    def resolve_action(self, action_key: str, state) -> None:
        if action_key == "disarm_trap" and not self._cleared:
            if self._rng.random() < 0.5:
                state.bus.publish(Message(text="You successfully disarmed the trap!"))
                found_item = self._rng.choice(["healing_potion", "mystery_potion", "bomb"])
                state.player.add_item(found_item, source=self.name, event_bus=state.bus)
                state.bus.publish(Message(text=f"You found a {found_item} while disarming the trap!"))
            else:
                damage_amount = self._rng.randint(15, 40)
                state.player.take_damage(damage_amount, source=self.name, event_bus=state.bus)
                state.bus.publish(Message(text=f"You triggered a trap and took {damage_amount} damage!"))
            self._cleared = True
            return

        if action_key == "leave" and not self._cleared:
            state.bus.publish(Message(text="You chose to leave the trap alone."))
            self._cleared = True

    def is_cleared(self) -> bool:
        return self._cleared
