from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.dungeon import GameState


class Item(Protocol):
    name: str
    display_name: str
    description: str

    def apply(self, state: "GameState") -> bool: ...
