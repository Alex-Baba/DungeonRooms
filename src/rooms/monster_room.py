from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence
import random

from .base import Action, SimpleAction
from ..events import Message


@dataclass
class Monster:
    hp: int
    attack: int

    def is_dead(self) -> bool:
        return self.hp <= 0


class MonsterRoom:
    name = "Monster Room"

    def __init__(self, rng: random.Random) -> None:
        self._cleared = False
        self._rng = rng

        count = self._rng.randint(1, 3)
        self.monsters: List[Monster] = [
            Monster(hp=self._rng.randint(20, 35), attack=self._rng.randint(6, 12))
            for _ in range(count)
        ]

    def _alive(self) -> List[Monster]:
        return [m for m in self.monsters if not m.is_dead()]

    def monsters_status(self) -> str:
        alive = self._alive()
        if not alive:
            return "Monsters: none"
        hps = ", ".join(str(m.hp) for m in alive)
        return f"Monsters: {len(alive)} alive | HP: [{hps}]"

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
        return [
            SimpleAction(key="fight_monster", description="Fight the monster"),
            SimpleAction(key="flee", description="Flee from the monster"),
            SimpleAction(key="use_item", description="Use an item from your inventory"),
        ]

    def resolve_action(self, action_key: str, state) -> None:
        if self._cleared:
            return

        handlers = {
            "fight_monster": self._handle_fight,
            "flee": self._handle_flee,
            "use_item": self._handle_use_item,
        }

        handler = handlers.get(action_key)
        if handler is None:
            state.bus.publish(Message(text="Invalid action."))
            return

        handler(state)

    def _handle_fight(self, state) -> None:
        alive = self._alive()
        if not alive:
            self._cleared = True
            return

        player_hit = self._rng.randint(12, 22)
        alive[0].hp = max(0, alive[0].hp - player_hit)
        state.bus.publish(Message(text=f"You strike a monster for {player_hit} damage."))

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
