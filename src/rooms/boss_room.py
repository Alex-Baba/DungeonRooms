from __future__ import annotations

import random
from typing import Sequence

from .base import Action, SimpleAction
from ..events import Message
from ..monsters import Monster, create_goblin_boss, create_slime_boss, create_wolf_boss


class BossRoom:
    name = "Boss Room"

    def __init__(self, rng: random.Random) -> None:
        self._cleared = False
        self._rng = rng
        boss_creators = [create_slime_boss, create_goblin_boss, create_wolf_boss]
        self.boss = rng.choice(boss_creators)(rng)

    def boss_status(self) -> str:
        if self.boss.is_dead():
            return "Boss: defeated"
        return f"Boss: {self.boss.name} ({self.boss.hp} HP)"

    def take_aoe_damage(self, amount: int, state) -> None:
        if self.boss.is_dead():
            state.bus.publish(Message(text="There is no boss to damage."))
            return

        self.boss.hp = max(0, self.boss.hp - amount)
        state.bus.publish(Message(text=f"The explosion hits the boss for {amount} damage!"))

        if self.boss.is_dead():
            state.bus.publish(Message(text="The boss has been defeated!"))
            self._cleared = True

    def get_actions(self) -> Sequence[Action]:
        actions: list[Action] = []
        if not self.boss.is_dead():
            actions.append(SimpleAction(key="attack_1", description=f"Attack {self.boss.name} (HP: {self.boss.hp})"))
        actions.append(SimpleAction(key="use_item", description="Use an item from your inventory"))
        return actions

    def resolve_action(self, action_key: str, state) -> None:
        if self._cleared:
            return

        if action_key == "use_item":
            self._handle_use_item(state)
            return

        if action_key in ("attack_1", "attack_boss"):
            self._handle_attack(state)
            return

        state.bus.publish(Message(text="Invalid action."))

    def _handle_attack(self, state) -> None:
        if self.boss.is_dead():
            self._cleared = True
            return

        player_hit = self._rng.randint(12, 22)
        self.boss.hp = max(0, self.boss.hp - player_hit)
        state.bus.publish(Message(text=f"You strike the boss for {player_hit} damage."))

        if self.boss.is_dead():
            state.bus.publish(Message(text="The boss has been defeated!"))
            self._cleared = True
            return

        state.player.take_damage(self.boss.attack, source=self.name, event_bus=state.bus)
        state.bus.publish(Message(text=f"The boss hits back for {self.boss.attack} damage!"))

    def _handle_use_item(self, state) -> None:
        if not state.player.inventory:
            state.bus.publish(Message(text="Your inventory is empty."))
            return

        state.bus.publish(Message(text=f"Your inventory: {', '.join(state.player.see_items())}"))
        item_name = input("Enter the name of the item to use: ").strip()
        if state.player.use_item(item_name, state):
            state.bus.publish(Message(text=f"You used {item_name} successfully!"))

    def is_cleared(self) -> bool:
        return self._cleared
