from __future__ import annotations

import random

from .base import Monster


def create_wolf_boss(rng: random.Random) -> Monster:
    """A wolf boss with balanced stats."""
    return Monster(name="Wolf Alpha", hp=rng.randint(65, 85), attack=rng.randint(11, 18))
