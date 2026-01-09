from __future__ import annotations

import random

from src.core import GameState, Player
from src.events import EventBus
from src.rooms import MonsterRoom, StartRoom


def test_bomb_deals_aoe_damage_to_all_monsters() -> None:
    rng = random.Random(0)
    room = MonsterRoom(rng)

    before = [m.hp for m in room.monsters]
    assert len(before) >= 1

    bus = EventBus()
    player = Player(name="Hero", health=100, gold=0, inventory=["bomb"])
    state = GameState(player=player, bus=bus, rng=rng, rooms=[StartRoom(), room], index=1)

    ok = player.use_item("bomb", state)

    assert ok is True
    assert player.inventory == []

    after = [m.hp for m in room.monsters]
    expected = [max(0, hp - 8) for hp in before]
    assert after == expected
