from __future__ import annotations

from typing import Sequence

from .base import Action, SimpleAction
from ..events import Message


class ShopRoom:
    name = "Shop Room"

    def __init__(self) -> None:
        self._cleared = False

        # Prices are intentionally simple + fixed.
        self._prices: dict[str, int] = {
            "healing_potion": 20,
            "mystery_potion": 30,
            "bomb": 25,
        }

    def shop_status(self) -> str:
        return "Shop: healing_potion(20g), bomb(25g), mystery_potion(30g)"

    def get_actions(self) -> Sequence[Action]:
        return [
            SimpleAction(key="buy_healing_potion", description="Buy Healing Potion (20 gold)"),
            SimpleAction(key="buy_bomb", description="Buy Bomb (25 gold)"),
            SimpleAction(key="buy_mystery_potion", description="Buy Mystery Potion (30 gold)"),
            SimpleAction(key="leave", description="Leave the shop"),
        ]

    def resolve_action(self, action_key: str, state) -> None:
        if self._cleared:
            return

        if action_key == "leave":
            state.bus.publish(Message(text="You leave the shop."))
            self._cleared = True
            return

        mapping = {
            "buy_healing_potion": "healing_potion",
            "buy_bomb": "bomb",
            "buy_mystery_potion": "mystery_potion",
        }

        item_name = mapping.get(action_key)
        if item_name is None:
            state.bus.publish(Message(text="Invalid action."))
            return

        price = self._prices[item_name]
        if state.player.gold < price:
            state.bus.publish(Message(text=f"Not enough gold. {item_name} costs {price} gold."))
            return

        state.player.gold -= price
        state.player.add_item(item_name, source=self.name, event_bus=state.bus)
        state.bus.publish(Message(text=f"Purchased {item_name} for {price} gold."))

    def is_cleared(self) -> bool:
        return self._cleared
