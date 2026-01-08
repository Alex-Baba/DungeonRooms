from __future__ import annotations

import random

from .base import Monster


def create_slime_boss(rng: random.Random) -> Monster:
    """A tougher slime boss with higher HP and damage."""
    return Monster(name="Slime King", hp=rng.randint(70, 95), attack=rng.randint(10, 16))
