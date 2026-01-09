from __future__ import annotations

from .event_bus import EventBus
from .types import (
    DamageTaken,
    GameLost,
    GameWon,
    GoldGained,
    Healed,
    ItemAcquired,
    ItemUsed,
    Message,
    PotionUsed,
    RoomEntered,
)


class ConsoleLogger:
    """Logs events to the console."""

    def __init__(self, event_bus: EventBus) -> None:
        event_bus.subscribe(RoomEntered, self.log_room_entered)
        event_bus.subscribe(DamageTaken, self.log_damage_taken)
        event_bus.subscribe(Healed, self.log_healed)
        event_bus.subscribe(GoldGained, self.log_gold_gained)
        event_bus.subscribe(ItemAcquired, self.log_item_acquired)
        event_bus.subscribe(PotionUsed, self.log_potion_used)
        event_bus.subscribe(ItemUsed, self.log_item_used)
        event_bus.subscribe(Message, self.log_message)
        event_bus.subscribe(GameWon, self.log_game_won)
        event_bus.subscribe(GameLost, self.log_game_lost)

    def log_room_entered(self, event: RoomEntered) -> None:
        print("\n" + "=" * 34)
        print(f"  {event.room_name}")
        print("=" * 34)

    def log_damage_taken(self, event: DamageTaken) -> None:
        print(f"  -{event.amount} HP   ({event.source})")

    def log_healed(self, event: Healed) -> None:
        print(f"  +{event.amount} HP   ({event.source})")

    def log_gold_gained(self, event: GoldGained) -> None:
        print(f"  +{event.amount} gold ({event.source})")

    def log_item_acquired(self, event: ItemAcquired) -> None:
        print(f"  + item: {event.item_name} ({event.source})")

    def log_potion_used(self, event: PotionUsed) -> None:
        print(f"Potion used: {event.potion_name} with effect {event.effect}")

    def log_item_used(self, event: ItemUsed) -> None:
        print(f"Item used: {event.item_name} with effect {event.effect}")

    def log_message(self, event: Message) -> None:
        print(f"  {event.text}")

    def log_game_won(self, event: GameWon) -> None:
        print("\nYou escaped the dungeon. You win!")

    def log_game_lost(self, event: GameLost) -> None:
        reason = getattr(event, "reason", None)
        if reason:
            print(f"\nGame over: {reason}")
        else:
            print("\nGame over.")
