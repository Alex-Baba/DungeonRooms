from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..events import Message

if TYPE_CHECKING:
    from ..core.dungeon import GameState


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
