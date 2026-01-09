from __future__ import annotations

import random

from src.core import GameState, Player
from src.events import EventBus
from src.events.types import DamageTaken, GameLost, Healed, PotionUsed
from src.rooms import StartRoom


def test_player_take_damage_publishes_events_and_game_lost_on_death() -> None:
    bus = EventBus()
    damage_events: list[DamageTaken] = []
    lost_events: list[GameLost] = []

    bus.subscribe(DamageTaken, damage_events.append)
    bus.subscribe(GameLost, lost_events.append)

    player = Player(name="Hero", health=5, gold=0, inventory=[])
    player.take_damage(5, source="Test", event_bus=bus)

    assert player.health == 0
    assert len(damage_events) == 1
    assert damage_events[0].amount == 5
    assert damage_events[0].source == "Test"
    assert len(lost_events) == 1


def test_player_use_item_consumes_item_and_publishes_potion_used() -> None:
    bus = EventBus()
    potion_events: list[PotionUsed] = []
    heal_events: list[Healed] = []
    bus.subscribe(PotionUsed, potion_events.append)
    bus.subscribe(Healed, heal_events.append)

    player = Player(name="Hero", health=50, gold=0, inventory=["healing_potion"])
    state = GameState(player=player, bus=bus, rng=random.Random(0), rooms=[StartRoom()])

    ok = player.use_item("healing_potion", state)

    assert ok is True
    assert "healing_potion" not in player.inventory
    assert player.health == 70
    assert len(heal_events) == 1
    assert len(potion_events) == 1
    assert potion_events[0].potion_name == "healing_potion"


class _FixedChoiceRng:
    def __init__(self, fixed: str) -> None:
        self._fixed = fixed

    def choice(self, seq):  # type: ignore[no-untyped-def]
        return self._fixed


def test_mystery_potion_heal_path_is_deterministic() -> None:
    bus = EventBus()
    potion_events: list[PotionUsed] = []
    heal_events: list[Healed] = []
    damage_events: list[DamageTaken] = []

    bus.subscribe(PotionUsed, potion_events.append)
    bus.subscribe(Healed, heal_events.append)
    bus.subscribe(DamageTaken, damage_events.append)

    player = Player(name="Hero", health=50, gold=0, inventory=["mystery_potion"])
    state = GameState(player=player, bus=bus, rng=_FixedChoiceRng("heal"), rooms=[StartRoom()])

    ok = player.use_item("mystery_potion", state)

    assert ok is True
    assert player.health == 65
    assert player.inventory == []
    assert len(heal_events) == 1
    assert heal_events[0].amount == 15
    assert len(damage_events) == 0
    assert len(potion_events) == 1
    assert potion_events[0].potion_name == "mystery_potion"


def test_mystery_potion_damage_path_is_deterministic() -> None:
    bus = EventBus()
    potion_events: list[PotionUsed] = []
    heal_events: list[Healed] = []
    damage_events: list[DamageTaken] = []

    bus.subscribe(PotionUsed, potion_events.append)
    bus.subscribe(Healed, heal_events.append)
    bus.subscribe(DamageTaken, damage_events.append)

    player = Player(name="Hero", health=50, gold=0, inventory=["mystery_potion"])
    state = GameState(player=player, bus=bus, rng=_FixedChoiceRng("damage"), rooms=[StartRoom()])

    ok = player.use_item("mystery_potion", state)

    assert ok is True
    assert player.health == 40
    assert player.inventory == []
    assert len(heal_events) == 0
    assert len(damage_events) == 1
    assert damage_events[0].amount == 10
    assert len(potion_events) == 1
    assert potion_events[0].potion_name == "mystery_potion"
