from __future__ import annotations

from dataclasses import dataclass
from typing import List
import random

from .player import Player
from .events import EventBus
from .rooms.base import Room
from .rooms import BossRoom, ExitRoom, MonsterRoom, RestRoom, ShopRoom, StartRoom, TrapRoom, TreasureRoom


@dataclass
class GameState:
    player: Player
    bus: EventBus
    rng: random.Random
    rooms: List[Room]
    index: int = 0
    won: bool = False

    def current_room(self) -> Room:
        return self.rooms[self.index]

    def advance(self) -> None:
        self.index += 1


class RoomFactory:
    """Factory Method: creates concrete room objects by room_type."""

    def create_room(self, room_type: str, rng: random.Random) -> Room:
        if room_type == "start":
            return StartRoom()
        if room_type == "exit":
            return ExitRoom()
        if room_type == "treasure":
            return TreasureRoom(rng)
        if room_type == "rest":
            return RestRoom(rng)
        if room_type == "trap":
            return TrapRoom(rng)
        if room_type == "monster":
            return MonsterRoom(rng)
        if room_type == "shop":
            return ShopRoom()
        if room_type == "boss":
            return BossRoom(rng)
        raise ValueError(f"Unknown room type: {room_type}")


def generate_dungeon(rng: random.Random, room_factory: RoomFactory, middle_rooms: int = 6) -> List[Room]:
    room_types = ["treasure", "rest", "trap", "monster"]
    weights = [0.3, 0.2, 0.25, 0.25]

    rooms: List[Room] = [StartRoom()]
    for _ in range(middle_rooms):
        room_type = rng.choices(room_types, weights=weights, k=1)[0]
        rooms.append(room_factory.create_room(room_type, rng))
    rooms.append(room_factory.create_room("shop", rng))
    rooms.append(room_factory.create_room("boss", rng))
    rooms.append(ExitRoom())
    return rooms