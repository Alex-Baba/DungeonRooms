from .base import Monster
from .goblin import create_goblin
from .goblin_boss import create_goblin_boss
from .slime import create_slime
from .slime_boss import create_slime_boss
from .wolf_boss import create_wolf_boss

__all__ = [
	"Monster",
	"create_goblin",
	"create_goblin_boss",
	"create_slime",
	"create_slime_boss",
	"create_wolf_boss",
]
