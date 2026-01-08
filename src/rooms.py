from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, DefaultDict, Dict, List, Type, Protocol, Sequence
import random


from .player import Player
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

    def resolve_action(self, action_key: str, state: GameState) -> None:
        if action_key == "open_chest" and not self._cleared:
            items = ["healing_potion", "mystery_potion", "bomb"]
            found_item = self._rng.choice(items)
            state.player.add_item(found_item, source=self.name, event_bus=state.bus)
            gold_amount = self._rng.randint(10, 100)
            state.player.add_gold(gold_amount, source=self.name, event_bus=state.bus)
            state.bus.publish(Message(text="You open the chest."))

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
        return [SimpleAction(key="disarm_trap", description="Attempt to disarm the trap"),
        SimpleAction(key="leave", description="Leave the trap"),
        ]

    def resolve_action(self, action_key:str, state:GameState)->None:
        if action_key == "disarm_trap" and not self._cleared:
            if self._rng.random() < 0.5:
                state.bus.publish(Message(text="You successfully disarmed the trap!"))
                found_item = self._rng.choice(["healing_potion", "mystery_potion", "bomb"])
                state.player.add_item(found_item, source=self.name, event_bus=state.bus)
                state.bus.publish(Message(text=f"You found a {found_item} while disarming the trap!"))
            else:
                damage_amount = self._rng.randint(15, 40)
                state.player.take_damage(damage_amount, source=self.name, event_bus=state.bus)
                state.bus.publish(Message(text=f"You triggered a trap and took {damage_amount} damage!"))
            self._cleared = True
        elif action_key == "leave" and not self._cleared:
            state.bus.publish(Message(text="You chose to leave the trap alone."))
            self._cleared = True

    def is_cleared(self)->bool:
        return self._cleared

@dataclass
class Monster:
    hp: int
    attack: int

    def is_dead(self) -> bool:
        return self.hp <= 0


class MonsterRoom:
    name = "Monster Room"

    def __init__(self, rng: random.Random) -> None:
        self._cleared = False
        self._rng = rng

        # Create 1–3 monsters so AoE items make sense
        count = self._rng.randint(1, 3)
        self.monsters: List[Monster] = [
            Monster(hp=self._rng.randint(20, 35), attack=self._rng.randint(6, 12))
            for _ in range(count)
        ]

    def _alive(self) -> List[Monster]:
        return [m for m in self.monsters if not m.is_dead()]

    def take_aoe_damage(self, amount: int, state: GameState) -> None:
        alive = self._alive()
        if not alive:
            state.bus.publish(Message(text="There are no monsters to damage."))
            return

        for m in alive:
            m.hp = max(0, m.hp - amount)

        state.bus.publish(Message(text=f"The bomb explodes! All monsters take {amount} damage."))

        if not self._alive():
            state.bus.publish(Message(text="All monsters are defeated!"))
            self._cleared = True

    def get_actions(self) -> Sequence[Action]:
        return [
            SimpleAction(key="fight_monster", description="Fight the monster"),
            SimpleAction(key="flee", description="Flee from the monster"),
            SimpleAction(key="use_item", description="Use an item from your inventory"),
        ]

    def resolve_action(self, action_key: str, state: GameState) -> None:
        if self._cleared:
            return

        handlers = {
            "fight_monster": self._handle_fight,
            "flee": self._handle_flee,
            "use_item": self._handle_use_item,
        }

        handler = handlers.get(action_key)
        if handler is None:
            state.bus.publish(Message(text="Invalid action."))
            return

        handler(state)

    def _handle_fight(self, state: GameState) -> None:
        alive = self._alive()
        if not alive:
            self._cleared = True
            return

        player_hit = self._rng.randint(12, 22)
        alive[0].hp = max(0, alive[0].hp - player_hit)
        state.bus.publish(Message(text=f"You strike a monster for {player_hit} damage."))

        if not self._alive():
            state.bus.publish(Message(text="All monsters are defeated!"))
            self._cleared = True
            return

        total = sum(m.attack for m in self._alive())
        state.player.take_damage(total, source=self.name, event_bus=state.bus)
        state.bus.publish(Message(text=f"The monsters hit back for {total} total damage!"))

    def _handle_flee(self, state: GameState) -> None:
        if self._rng.random() < 0.5:
            state.bus.publish(Message(text="You successfully fled from the monsters!"))
        else:
            damage_amount = self._rng.randint(10, 30)
            state.player.take_damage(damage_amount, source=self.name, event_bus=state.bus)
            state.bus.publish(Message(text=f"You failed to flee and took {damage_amount} damage!"))
        self._cleared = True

    def _handle_use_item(self, state: GameState) -> None:
        if not state.player.inventory:
            state.bus.publish(Message(text="Your inventory is empty."))
            return

        state.bus.publish(Message(text=f"Your inventory: {', '.join(state.player.see_items())}"))
        item_name = input("Enter the name of the item to use: ").strip()
        if state.player.use_item(item_name, state):
            state.bus.publish(Message(text=f"You used {item_name} successfully!"))

    def is_cleared(self) -> bool:
        return self._cleared

    def monsters_status(self) -> str:
        alive = self._alive()
        if not alive:
            return "Monsters: none"
        hps = ", ".join(str(m.hp) for m in alive)
        return f"Monsters: {len(alive)} alive | HP: [{hps}]"

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