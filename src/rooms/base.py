from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.dungeon import GameState


class Action(Protocol):
    key: str
    description: str


@dataclass(frozen=True)
class SimpleAction:
    key: str
    description: str


class Room(Protocol):
    name: str

    def get_actions(self) -> Sequence[Action]: ...

    def resolve_action(self, action_key: str, state: GameState) -> None: ...

    def is_cleared(self) -> bool: ...
