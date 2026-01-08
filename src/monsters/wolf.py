from __future__ import annotations

import random

from .base import Monster

def create_wolf(rng: random.Random) -> Monster:
    """A swift and cunning wolf monster."""
    return Monster(name="Wolf", hp=rng.randint(20, 30), attack=rng.randint(6, 11))