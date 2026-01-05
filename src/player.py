from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, DefaultDict, Dict, List, Type

from .events import (
    RoomEntered,
    DamageTaken,
    Healed,
    GoldGained,
    ItemAcquired,
    PotionUsed,
    Message,
    GameWon,
    GameLost,
    EventBus,
)


@dataclass
class Player:
    name: str
    health: int
    gold: int
    inventory: List[str]

    def is_dead(self) -> bool:
        return self.health <= 0

    def take_damage(self,amount:int, source:str, event_bus:EventBus)->None:
        self.health -= amount
        event_bus.publish(DamageTaken(amount=amount, source=source))
        if self.is_dead():
            event_bus.publish(GameLost(reason=f"{self.name} has died."))

    def heal(self,amount:int, source:str, event_bus:EventBus)->None:
        self.health += amount
        event_bus.publish(Healed(amount=amount, source=source))