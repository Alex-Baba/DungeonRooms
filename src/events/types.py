from __future__ import annotations

from dataclasses import dataclass

#frozen is True to make instances immutable
@dataclass(frozen=True)
class RoomEntered:
    room_name: str


@dataclass(frozen=True)
class DamageTaken:
    amount: int
    source: str


@dataclass(frozen=True)
class Healed:
    amount: int
    source: str


@dataclass(frozen=True)
class GoldGained:
    amount: int
    source: str = "unknown"


@dataclass(frozen=True)
class ItemAcquired:
    item_name: str
    source: str


@dataclass(frozen=True)
class PotionUsed:
    potion_name: str
    effect: str


@dataclass(frozen=True)
class ItemUsed:
    item_name: str
    effect: str


@dataclass(frozen=True)
class Message:
    text: str


@dataclass(frozen=True)
class GameWon:
    pass


@dataclass(frozen=True)
class GameLost:
    reason: str = "unknown"
