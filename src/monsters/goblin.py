from __future__ import annotations

import random

from .base import Monster


def create_goblin(rng: random.Random) -> Monster:
    """Fast, moderate damage."""
    return Monster(name="Goblin", hp=rng.randint(18, 28), attack=rng.randint(7, 12))
