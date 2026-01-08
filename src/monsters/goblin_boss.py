from __future__ import annotations

import random

from .base import Monster


def create_goblin_boss(rng: random.Random) -> Monster:
    """A goblin boss with higher damage."""
    return Monster(name="Goblin Chief", hp=rng.randint(55, 75), attack=rng.randint(13, 20))
