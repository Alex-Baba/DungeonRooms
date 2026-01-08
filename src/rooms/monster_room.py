from __future__ import annotations

from typing import List, Sequence
import random

from .base import Action, SimpleAction
from ..events import Message
from ..monsters import Monster, create_goblin, create_slime,create_wolf

class MonsterRoom:
    name = "Monster Room"

    def __init__(self, rng: random.Random) -> None:
        self._cleared = False
        self._rng = rng

        count = self._rng.randint(1, 3)
        creators = [create_goblin, create_slime, create_wolf]
        self.monsters: List[Monster] = [self._rng.choice(creators)(self._rng) for _ in range(count)]

    def _alive(self) -> List[Monster]:
        return [m for m in self.monsters if not m.is_dead()]

    def monsters_status(self) -> str:
        alive = self._alive()
        if not alive:
            return "Monsters: none"
        summary = ", ".join(f"{i + 1}:{m.name}({m.hp} HP)" for i, m in enumerate(alive))
        return f"Monsters: {len(alive)} alive | {summary}"

    def take_aoe_damage(self, amount: int, state) -> None:
        alive = self._alive()
        if not alive:
            state.bus.publish(Message(text="There are no monsters to damage."))
            return

        for m in alive:
            m.hp = max(0, m.hp - amount)

        state.bus.publish(Message(text=f"The bomb explodes! All monsters take {amount} damage."))

        if not self._alive():
            state.bus.publish(Message(text="All monsters are defeated!"))
            self._cleared = True

    def get_actions(self) -> Sequence[Action]:
        actions: List[Action] = []

        alive = self._alive()
        for i, monster in enumerate(alive, start=1):
            actions.append(
                SimpleAction(
                    key=f"attack_{i}",
                    description=f"Attack {monster.name} (HP: {monster.hp})",
                )
            )
        actions.append(SimpleAction(key="flee", description="Flee from the monsters"))
        actions.append(SimpleAction(key="use_item", description="Use an item from your inventory"))
        return actions

    def resolve_action(self, action_key: str, state) -> None:
        if self._cleared:
            return

        if action_key.startswith("attack_"):
            suffix = action_key.removeprefix("attack_")
            if not suffix.isdigit():
                state.bus.publish(Message(text="Invalid attack target."))
                return
            target_index = int(suffix) - 1
            self._handle_attack(state, target_index)
            return

        handlers = {
            "flee": self._handle_flee,
            "use_item": self._handle_use_item,
        }

        handler = handlers.get(action_key)
        if handler is None:
            state.bus.publish(Message(text="Invalid action."))
            return

        handler(state)

    def _handle_attack(self, state, target_index: int) -> None:
        alive = self._alive()
        if not alive:
            self._cleared = True
            return

        if target_index < 0 or target_index >= len(alive):
            state.bus.publish(Message(text="That monster target does not exist."))
            return

        player_hit = self._rng.randint(12, 22)
        target = alive[target_index]
        target.hp = max(0, target.hp - player_hit)
        state.bus.publish(Message(text=f"You strike the {target.name} for {player_hit} damage."))

        if not self._alive():
            state.bus.publish(Message(text="All monsters are defeated!"))
            self._cleared = True
            return

        total = sum(m.attack for m in self._alive())
        state.player.take_damage(total, source=self.name, event_bus=state.bus)
        state.bus.publish(Message(text=f"The monsters hit back for {total} total damage!"))

    def _handle_flee(self, state) -> None:
        if self._rng.random() < 0.5:
            state.bus.publish(Message(text="You successfully fled from the monsters!"))
        else:
            damage_amount = self._rng.randint(10, 30)
            state.player.take_damage(damage_amount, source=self.name, event_bus=state.bus)
            state.bus.publish(Message(text=f"You failed to flee and took {damage_amount} damage!"))
        self._cleared = True

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
