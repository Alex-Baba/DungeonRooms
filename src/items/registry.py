from __future__ import annotations

from typing import Dict, Optional

from .types import Item
from .potions import HealingPotion, MysteryPotion
from .bomb import Bomb

ITEMS: Dict[str, Item] = {
    "healing_potion": HealingPotion(),
    "mystery_potion": MysteryPotion(),
    "bomb": Bomb(),
}


def get_item_by_name(name: str) -> Optional[Item]:
    return ITEMS.get(name)
