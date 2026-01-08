from __future__ import annotations

import random
import argparse

try:
    # Preferred: run as a package module: `python -m src.app`
    from .dungeon import GameState, generate_dungeon, RoomFactory
    from .player import Player
    from .events import EventBus, Message, ConsoleLogger, RoomEntered
except ImportError:  # pragma: no cover
    # Fallback: allow running the file directly: `python src/app.py`
    from pathlib import Path
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[1]))

    from src.dungeon import GameState, generate_dungeon, RoomFactory
    from src.player import Player
    from src.events import EventBus, Message, ConsoleLogger, RoomEntered


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument("--rooms", type=int, default=6, help="Number of rooms in the game")
    return parser.parse_args()


def _prompt_optional_int(prompt: str, default: int | None) -> int | None:
    default_text = "none" if default is None else str(default)
    while True:
        raw = input(f"{prompt} [{default_text}]: ").strip()
        if raw == "":
            return default
        if raw.lower() in ("none", "null"):
            return None
        try:
            return int(raw)
        except ValueError:
            print("Please enter an integer (or press Enter for default).")


def _prompt_positive_int(prompt: str, default: int) -> int:
    while True:
        raw = input(f"{prompt} [{default}]: ").strip()
        if raw == "":
            return default
        try:
            value = int(raw)
        except ValueError:
            print("Please enter an integer (or press Enter for default).")
            continue
        if value <= 0:
            print("Please enter a positive integer.")
            continue
        return value


def _setup_game(args: argparse.Namespace) -> tuple[GameState, EventBus]:
    rng = random.Random(args.seed)
    event_bus = EventBus()
    ConsoleLogger(event_bus)

    state = GameState(
        player=Player(name="Hero", health=100, gold=0, inventory=[]),
        bus=event_bus,
        rng=rng,
        rooms=generate_dungeon(rng, RoomFactory(), args.rooms),
    )
    return state, event_bus


def _publish_room_info(event_bus: EventBus, state: GameState, room) -> None:
    event_bus.publish(RoomEntered(room_name=room.name))
    event_bus.publish(Message(text=f"You are in {room.name}."))
    event_bus.publish(Message(text=f"Your health: {state.player.health}, Gold: {state.player.gold}"))

    for status_attr in ("monsters_status", "boss_status"):
        status_fn = getattr(room, status_attr, None)
        if callable(status_fn):
            event_bus.publish(Message(text=status_fn()))


def _print_actions(room) -> None:
    for action in room.get_actions():
        print(f"{action.key}: {action.description}")


def _run_turn(state: GameState, event_bus: EventBus) -> None:
    room = state.current_room()
    _publish_room_info(event_bus, state, room)
    _print_actions(room)
    choice = input("Choose an action: ").strip()
    room.resolve_action(choice, state)
    if room.is_cleared():
        state.advance()
        if state.index >= len(state.rooms):
            state.won = True


def main() -> int:
    args = _parse_args()

    # Let the user choose settings interactively after starting the app.
    print("\nDungeon setup (press Enter to accept defaults)")
    args.seed = _prompt_optional_int("Seed", args.seed)
    args.rooms = _prompt_positive_int("Number of random rooms", args.rooms)

    state, event_bus = _setup_game(args)

    while not state.player.is_dead() and not state.won:
        _run_turn(state, event_bus)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())