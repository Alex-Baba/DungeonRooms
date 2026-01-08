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
            SimpleAction(key="disarm_trap", description="Disarm (high risk / high reward)"),
            SimpleAction(key="careful_disarm", description="Careful disarm (lower risk / lower reward)"),
            SimpleAction(key="tank_trap", description="Walk through (guaranteed damage, guaranteed loot)"),
            SimpleAction(key="leave", description="Leave the trap"),
        ]

    def resolve_action(self, action_key: str, state) -> None:
        if self._cleared:
            return

        loot_items = ["healing_potion", "mystery_potion", "bomb"]

        if action_key == "disarm_trap":
            # High risk / high reward
            if self._rng.random() < 0.5:
                state.bus.publish(Message(text="You successfully disarmed the trap!"))
                found_item = self._rng.choice(loot_items)
                state.player.add_item(found_item, source=self.name, event_bus=state.bus)
                gold_amount = self._rng.randint(10, 35)
                state.player.add_gold(gold_amount, source=self.name, event_bus=state.bus)
            else:
                damage_amount = self._rng.randint(15, 40)
                state.player.take_damage(damage_amount, source=self.name, event_bus=state.bus)
                state.bus.publish(Message(text=f"You triggered the trap and took {damage_amount} damage!"))
            self._cleared = True
            return

        if action_key == "careful_disarm":
            # Lower risk / lower reward
            if self._rng.random() < 0.75:
                state.bus.publish(Message(text="You carefully disarm the trap."))
                if self._rng.random() < 0.4:
                    found_item = self._rng.choice(loot_items)
                    state.player.add_item(found_item, source=self.name, event_bus=state.bus)
                gold_amount = self._rng.randint(5, 15)
                state.player.add_gold(gold_amount, source=self.name, event_bus=state.bus)
            else:
                damage_amount = self._rng.randint(5, 12)
                state.player.take_damage(damage_amount, source=self.name, event_bus=state.bus)
                state.bus.publish(Message(text=f"You slip up and take {damage_amount} damage."))
            self._cleared = True
            return

        if action_key == "tank_trap":
            # Guaranteed damage, guaranteed loot
            damage_amount = self._rng.randint(8, 18)
            state.player.take_damage(damage_amount, source=self.name, event_bus=state.bus)
            state.bus.publish(Message(text=f"You push through and take {damage_amount} damage."))
            found_item = self._rng.choice(loot_items)
            state.player.add_item(found_item, source=self.name, event_bus=state.bus)
            gold_amount = self._rng.randint(10, 25)
            state.player.add_gold(gold_amount, source=self.name, event_bus=state.bus)
            self._cleared = True
            return

        if action_key == "leave":
            state.bus.publish(Message(text="You chose to leave the trap alone."))
            self._cleared = True
            return

        state.bus.publish(Message(text="Invalid action."))

    def is_cleared(self) -> bool:
        return self._cleared
