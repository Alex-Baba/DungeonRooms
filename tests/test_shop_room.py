from __future__ import annotations

import random

from src.core import GameState, Player
from src.events import EventBus
from src.events.types import ItemAcquired
from src.rooms import ShopRoom


def test_shop_purchase_spends_gold_and_adds_item() -> None:
    bus = EventBus()
    acquired: list[ItemAcquired] = []
    bus.subscribe(ItemAcquired, acquired.append)

    player = Player(name="Hero", health=100, gold=25, inventory=[])
    room = ShopRoom()
    state = GameState(player=player, bus=bus, rng=random.Random(0), rooms=[room])

    room.resolve_action("buy_bomb", state)

    assert player.gold == 0
    assert player.inventory == ["bomb"]
    assert len(acquired) == 1
    assert acquired[0].item_name == "bomb"
    assert acquired[0].source == "Shop Room"
