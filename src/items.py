from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Protocol, TYPE_CHECKING

from .events import Message

if TYPE_CHECKING:
    from .dungeon import GameState


class Item(Protocol):
    name: str
    display_name: str
    description: str

    def apply(self, state: "GameState") -> bool: ...


@dataclass(frozen=True)
class HealingPotion:
    name: str = "healing_potion"
    display_name: str = "Healing Potion"
    description: str = "A potion that restores 20 health points."

    def apply(self, state: "GameState") -> bool:
        state.player.heal(20, source=self.display_name, event_bus=state.bus)
        state.bus.publish(Message(text=f"{state.player.name} used {self.display_name} and restored 20 health points."))
        return True


@dataclass(frozen=True)
class MysteryPotion:
    name: str = "mystery_potion"
    display_name: str = "Mystery Potion"
    description: str = "A potion with unpredictable effects."

    def apply(self, state: GameState) -> bool:
        effect = state.rng.choice(["heal", "damage"])
        if effect == "heal":
            state.player.heal(15, source=self.display_name, event_bus=state.bus)
            state.bus.publish(Message(text=f"{state.player.name} used {self.display_name} and restored 15 health points."))
        else:
            state.player.take_damage(10, source=self.display_name, event_bus=state.bus)
            state.bus.publish(Message(text=f"{state.player.name} used {self.display_name} and took 10 damage!"))
        return True


@dataclass(frozen=True)
class Bomb:
    name: str = "bomb"
    display_name: str = "Bomb"
    description: str = "Deal 8 damage to all enemies in the current room."
    damage: int = 8

    def apply(self, state: "GameState") -> bool:
        room = state.current_room()

        if hasattr(room, "take_aoe_damage"):
            room.take_aoe_damage(self.damage, state)
            return True

        state.bus.publish(Message(text="Bomb had no effect in this room."))
        return False


ITEMS: Dict[str, Item] = {
    "healing_potion": HealingPotion(),
    "mystery_potion": MysteryPotion(),
    "bomb": Bomb(),
}

def get_item_by_name(name: str) -> Optional[Item]:
    return ITEMS.get(name)