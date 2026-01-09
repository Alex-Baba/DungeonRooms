from __future__ import annotations

import random

from src.core.dungeon import RoomFactory, generate_dungeon
from src.rooms import BossRoom, ExitRoom, ShopRoom, StartRoom


def test_generate_dungeon_has_expected_ordering() -> None:
    rng = random.Random(123)
    rooms = generate_dungeon(rng, RoomFactory(), middle_rooms=3)

    assert len(rooms) == 1 + 3 + 3  # start + middle + shop+boss+exit
    assert isinstance(rooms[0], StartRoom)
    assert isinstance(rooms[-3], ShopRoom)
    assert isinstance(rooms[-2], BossRoom)
    assert isinstance(rooms[-1], ExitRoom)
