from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..events import Message

if TYPE_CHECKING:
    from ..core.dungeon import GameState


@dataclass(frozen=True)
class HealingPotion:
    name: str = "healing_potion"
    display_name: str = "Healing Potion"
    description: str = "A potion that restores 20 health points."

    def apply(self, state: "GameState") -> bool:
        state.player.heal(20, source=self.display_name, event_bus=state.bus)
        state.bus.publish(
            Message(text=f"{state.player.name} used {self.display_name} and restored 20 health points.")
        )
        return True


@dataclass(frozen=True)
class MysteryPotion:
    name: str = "mystery_potion"
    display_name: str = "Mystery Potion"
    description: str = "A potion with unpredictable effects."

    def apply(self, state: "GameState") -> bool:
        effect = state.rng.choice(["heal", "damage"])
        if effect == "heal":
            state.player.heal(15, source=self.display_name, event_bus=state.bus)
            state.bus.publish(
                Message(text=f"{state.player.name} used {self.display_name} and restored 15 health points.")
            )
        else:
            state.player.take_damage(10, source=self.display_name, event_bus=state.bus)
            state.bus.publish(Message(text=f"{state.player.name} used {self.display_name} and took 10 damage!"))
        return True
