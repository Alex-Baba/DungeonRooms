from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, DefaultDict, Dict, List, Type

@dataclass(frozen=True)
class RoomEntered:
    room_name=str

@dataclass(frozen=True)
class DamageTaken:
    amount=int
    source=str

@dataclass(frozen=True)
class Healed:
    amount=int
    source=str

@dataclass(frozen=True)
class GoldGained:
    amount=int
    source=str

@dataclass(frozen=True)
class ItemAcquired:
    item_name=str
    source=str

@dataclass(frozen=True)
class PotionUsed:
    potion_name=str
    effect=str

@dataclass(frozen=True)
class Message:
    text=str

@dataclass(frozen=True)
class GameWon:
    pass

@dataclass(frozen=True)
class GameLost:
    reason=str

EventHandler = Callable[[Any], None]

class EventBus:
    """A simple event bus for managing event subscriptions and dispatching events."""
    def __init__(self)->None:
        self._subs: Dict[Type[Any], List[EventHandler]] = {}

    def subscribe(self, event_type: Type[Any], handler: EventHandler)->None:
        self._subs.setdefault(event_type, []).append(handler)

    def publish(self, event: Any)->None:
        for handler in self._subs.get(type(event), []):
            handler(event)

class ConsoleLogger:
    """Logs events to the console."""
    def __init__(self, event_bus: EventBus)->None:
        event_bus.subscribe(RoomEntered, self.log_room_entered)
        event_bus.subscribe(DamageTaken, self.log_damage_taken)
        event_bus.subscribe(Healed, self.log_healed)
        event_bus.subscribe(GoldGained, self.log_gold_gained)
        event_bus.subscribe(ItemAcquired, self.log_item_acquired)
        event_bus.subscribe(PotionUsed, self.log_potion_used)
        event_bus.subscribe(Message, self.log_message)
        event_bus.subscribe(GameWon, self.log_game_won)
        event_bus.subscribe(GameLost, self.log_game_lost)

    def log_room_entered(self, event: RoomEntered)->None:
        print(f"Entered room: {event.room_name}")

    def log_damage_taken(self, event: DamageTaken)->None:
        print(f"Damage taken: {event.amount} from {event.source}")

    def log_healed(self, event: Healed)->None:
        print(f"Healed: {event.amount} from {event.source}")

    def log_gold_gained(self, event: GoldGained)->None:
        print(f"Gold gained: {event.amount} from {event.source}")

    def log_item_acquired(self, event: ItemAcquired)->None:
        print(f"Item acquired: {event.item_name} from {event.source}")

    def log_potion_used(self, event: PotionUsed)->None:
        print(f"Potion used: {event.potion_name} with effect {event.effect}")

    def log_message(self, event: Message)->None:
        print(f"Message: {event.text}")

    def log_game_won(self, event: GameWon)->None:
        print("Game won!")

    def log_game_lost(self, event: GameLost)->None:
        print(f"Game lost! Reason: {event.reason}")