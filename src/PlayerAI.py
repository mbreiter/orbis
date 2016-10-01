from PythonClientAPI.libs.Game import PointUtils
from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Game.Entities import *
from PythonClientAPI.libs.Game.World import *


class PlayerAI:
    def __init__(self):
        pass

    def do_move(self, world, enemy_units, friendly_units):
        """
        This method will get called every turn; Your glorious AI code goes here.
        
        :param World world: The latest state of the world.
        :param list[EnemyUnit] enemy_units: An array of all 4 units on the enemy team. Their order won't change.
        :param list[FriendlyUnit] friendly_units: An array of all 4 units on your team. Their order won't change.
        """
        pass