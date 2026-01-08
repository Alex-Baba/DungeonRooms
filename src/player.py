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

from .items import get_item_by_name


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

    def add_gold(self,amount:int, source:str, event_bus:EventBus)->None:
        self.gold += amount
        event_bus.publish(GoldGained(amount=amount, source=source))

    def add_item(self,item_name:str, source:str, event_bus:EventBus)->None:
        self.inventory.append(item_name)
        event_bus.publish(ItemAcquired(item_name=item_name, source=source))

    def use_item(self,item_name:str, state:GameState)->bool:
        if item_name in self.inventory:
            item = get_item_by_name(item_name)
            if item and item.apply(state):
                self.inventory.remove(item_name)
                state.bus.publish(PotionUsed(potion_name=item_name, effect="used"))
                return True
        return False