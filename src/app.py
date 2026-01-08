from __future__ import annotations

import random
import argparse

from .rooms import GameState, Room, generate_dungeon, RoomFactory
from .player import Player
from .events import EventBus, Message, GameWon, ConsoleLogger, RoomEntered


def main() -> int:
    parser =argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument("--rooms",type=int, default=6, help="Number of rooms in the game")
    args =parser.parse_args()

    rng=random.Random(args.seed)
    event_bus=EventBus()
    ConsoleLogger(event_bus)

    state=GameState(
        player=Player(name="Hero", health=100, gold=0, inventory=[]),
        bus=event_bus,
        rng=rng,
        rooms=generate_dungeon(rng, RoomFactory(), args.rooms),
    )

    while True:
        if state.player.is_dead():
            print("You have perished. Game over.")
            break

        if state.won:
            print("Congratulations! You have won the game!")
            break

        room = state.current_room()
        event_bus.publish(RoomEntered(room_name=room.name))
        event_bus.publish(Message(text=f"You are in {room.name}."))
        event_bus.publish(Message(text=f"Your health: {state.player.health}, Gold: {state.player.gold}"))

        # Show monsters + HP if this room supports it
        if hasattr(room, "monsters_status"):
            event_bus.publish(Message(text=room.monsters_status()))

        actions = room.get_actions()
        for action in actions:
            print(f"{action.key}: {action.description}")
        choice=input("Choose an action: ").strip()
        room.resolve_action(choice, state)
        if room.is_cleared():
            state.advance()
            if state.index >= len(state.rooms):
                state.won = True
                #event_bus.publish(GameWon())

    return 0

if __name__ == "__main__":
    raise SystemExit(main())