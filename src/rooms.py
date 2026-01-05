from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, DefaultDict, Dict, List, Type, Protocol, Sequence
import random


from src.player import Player
from src.events import (
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
class GameState:
    player: Player
    bus : EventBus
    rng: random.Random
    rooms:List["Room"]
    index:int=0
    won:bool=False

    def current_room(self)->"Room":
        return self.rooms[self.index]

    def advance(self)->None:
        self.index += 1
        

class Action(Protocol):
    key: str
    description: str


@dataclass(frozen=True)
class SimpleAction:
    key:str
    description:str




class Room(Protocol):
    name : str

    def get_actions(self)->List[Action]:
        ...

    def resolve_action(self, action_key:str, state:GameState)->None:
        ...
    
    def is_cleared(self)->bool:
        ... 


class StartRoom:
    name="Start Room"

    def __init__(self)->None:
        self._cleared=False

    def get_actions(self)->Sequence[Action]:
        return [SimpleAction(key="proceed", description="Proceed to the next room")]

    def resolve_action(self, action_key:str, state:GameState)->None:
        if action_key == "proceed":
            state.bus.publish(Message(text="You proceed to the next room."))
            self._cleared = True

    def is_cleared(self)->bool:
        return self._cleared

class ExitRoom:
    name="Exit Room"

    def __init__(self)->None:
        self._cleared=False

    def get_actions(self)->Sequence[Action]:
        return [SimpleAction(key="exit", description="Exit the dungeon")]

    def resolve_action(self, action_key:str, state:GameState)->None:
        if action_key == "exit":
            state.bus.publish(Message(text="You exit the dungeon victorious!"))
            state.won = True
            state.bus.publish(GameWon())
            self._cleared = True

    def is_cleared(self)->bool:
        return self._cleared

class TreasureRoom:
    name="Treasure Room"

    def __init__(self,rng:random.Random)->None:
        self._cleared=False
        self._rng=rng

    def get_actions(self)->Sequence[Action]:
        return [SimpleAction(key="open_chest", description="Open the treasure chest")]

    def resolve_action(self, action_key:str, state:GameState)->None:
        if action_key == "open_chest" and not self._cleared:
            gold_amount = self._rng.randint(50, 200)
            state.player.gold += gold_amount
            state.bus.publish(GoldGained(amount=gold_amount, source=self.name))
            state.bus.publish(Message(text=f"You found {gold_amount} gold in the chest!"))
            self._cleared = True

    def is_cleared(self)->bool:
        return self._cleared

class RestRoom:
    name="Rest Room"

    def __init__(self,rng:random.Random)->None:
        self._cleared=False
        self._rng=rng

    def get_actions(self)->Sequence[Action]:
        return [SimpleAction(key="rest", description="Rest to recover health")]

    def resolve_action(self, action_key:str, state:GameState)->None:
        if action_key == "rest" and not self._cleared:
            heal_amount = self._rng.randint(10, 30)
            state.player.heal(heal_amount, source=self.name, event_bus=state.bus)
            state.bus.publish(Message(text=f"You rested and recovered {heal_amount} health!"))
            self._cleared = True

    def is_cleared(self)->bool:
        return self._cleared

class TrapRoom:
    name="Trap Room"

    def __init__(self,rng:random.Random)->None:
        self._cleared=False
        self._rng=rng

    def get_actions(self)->Sequence[Action]:
        return [SimpleAction(key="disarm_trap", description="Attempt to disarm the trap")]

    def resolve_action(self, action_key:str, state:GameState)->None:
        if action_key == "disarm_trap" and not self._cleared:
            damage_amount = self._rng.randint(15, 40)
            state.player.take_damage(damage_amount, source=self.name, event_bus=state.bus)
            state.bus.publish(Message(text=f"You triggered a trap and took {damage_amount} damage!"))
            self._cleared = True

    def is_cleared(self)->bool:
        return self._cleared

class MonsterRoom:
    name="Monster Room"

    def __init__(self,rng:random.Random)->None:
        self._cleared=False
        self._rng=rng

    def get_actions(self)->Sequence[Action]:
        return [SimpleAction(key="fight_monster", description="Fight the monster")]

    def resolve_action(self, action_key:str, state:GameState)->None:
        if action_key == "fight_monster" and not self._cleared:
            damage_amount = self._rng.randint(20, 50)
            state.player.take_damage(damage_amount, source=self.name, event_bus=state.bus)
            state.bus.publish(Message(text=f"You fought the monster and took {damage_amount} damage!"))
            self._cleared = True

    def is_cleared(self)->bool:
        return self._cleared


class RoomFactory:
    """Factory to create rooms for the dungeon."""
    def create_room(self, room_type:str, rng:random.Random)->object:
        if room_type == "start":
            return StartRoom()
        elif room_type == "exit":
            return ExitRoom()
        elif room_type == "treasure":
            return TreasureRoom(rng)
        elif room_type == "rest":
            return RestRoom(rng)
        elif room_type == "trap":
            return TrapRoom(rng)
        elif room_type == "monster":
            return MonsterRoom(rng)
        else:
            raise ValueError(f"Unknown room type: {room_type}")

def generate_dungeon(rng:random.Random, room_factory:RoomFactory,middle_rooms=6)->List[object]:
    room_types=["treasure", "rest", "trap", "monster"]
    weights=[0.3, 0.2, 0.25, 0.25]

    rooms : List[object] = [StartRoom()]
    for _ in range(middle_rooms):
        room_type=rng.choices(room_types, weights=weights,k=1)[0]
        rooms.append(room_factory.create_room(room_type, rng))
    rooms.append(ExitRoom())
    return rooms