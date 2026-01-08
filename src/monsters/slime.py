from __future__ import annotations

import random

from .base import Monster


def create_slime(rng: random.Random) -> Monster:
    """Tankier, lower damage."""
    return Monster(name="Slime", hp=rng.randint(25, 40), attack=rng.randint(4, 9))
