"""j5 Robotics API."""

from .backends.environment import Environment
from .base_robot import BaseRobot
from .boards import BoardGroup

__all__ = [
    "BoardGroup",
    "BaseRobot",
    "Environment",
    "__version__",
    "__version_short__",
]

__version__ = "1.0.0"
__version_short__ = "1.0.0"
