from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Monster:
    name: str
    hp: int
    attack: int

    def is_dead(self) -> bool:
        return self.hp <= 0
