import json
from collections import OrderedDict
from enum import Enum

from PythonClientAPI.libs.Game.PointUtils import sub_points, get_point_sign, add_points


class Direction(Enum):
    """
    Represents 8 cardinal directions that Units can move or shoot in.
    Their value is a coordinate offset represented by a single move of 1 tile in that direction.
    """
    NOWHERE = (0, 0)
    NORTH = (0, -1)
    NORTH_EAST = (1, -1)
    EAST = (1, 0)
    SOUTH_EAST = (1, 1)
    SOUTH = (0, 1)
    SOUTH_WEST = (-1, 1)
    WEST = (-1, 0)
    NORTH_WEST = (-1, -1)

    @classmethod
    def from_to(cls, from_point, to_point):
        """
        Calculates a direction between two points. The points do not have to be in a line, however the direction returned
        can only guarantee that it will move towards the 'to' point along the path with the minimum moves.

        NOTE: This does not use path finding, and calculates results "as the crow flies".

        :param (int,int) from_point: The point to start at
        :param (int,int) to_point: The point to move towards
        """
        delta = sub_points(to_point, from_point)
        return cls._delta_to_direction[get_point_sign(delta)]

    @classmethod
    def get_direction_from_vector(cls, vector):
        """
        Turns a vector into a direction.
        Any non-zero components will be normalized to 1 or -1.
        This means both (1, 1) and (1, 10) will become SOUTH_EAST, and both (-1, 0) and (-10, 0) will become WEST

        :param (int,int) vector:
        :rtype: Direction
        """
        return cls._delta_to_direction[vector]

    def move_point(self, point):
        """
        Returns a new point who's values are that of the given point moved 1 tile in this direction.

        :param (int,int) point:
        """
        return add_points(point, self.value)

    def rotate_clockwise(self, times):
        """
        Returns a direction representing a number of clockwise turns of this direction.

        For example, 1 turn of NORTH is NORTH_EAST, 2 turns of NORTH is EAST
        :param int times: he number of clockwise turns
        :rtype: Direction
        """
        if self == Direction.NOWHERE:
            return Direction.NOWHERE
        ordinal = Direction._rotation_list[self]
        mod = (ordinal + times) % 8

        # Should not be needed for python, but here just in case
        if mod < 0:
            mod += 8

        return list(Direction._rotation_list.keys())[mod]

    def rotate_counter_clockwise(self, times):
        """
        Returns a direction representing a number of clockwise turns of this direction.

        For example, 1 turn of NORTH is NORTH_EAST, 2 turns of NORTH is EAST
        :param int times: he number of clockwise turns
        :rtype: Direction
        """
        return self.rotate_clockwise(-times)


Direction._delta_to_direction = {
    dir.value: dir for dir in Direction
    }

Direction._rotation_list = OrderedDict([
    (Direction.NORTH, 0), (Direction.NORTH_EAST, 1), (Direction.EAST, 2), (Direction.SOUTH_EAST, 3),
    (Direction.SOUTH, 4),
    (Direction.SOUTH_WEST, 5), (Direction.WEST, 6), (Direction.NORTH_WEST, 7)
])


class TileType(Enum):
    WALL = 0
    FLOOR = 1
    AMBER_SPAWN = 2
    BLUE_SPAWN = 3

    def does_block_bullets(self):
        return self == TileType.WALL

    def does_block_movement(self):
        return self == TileType.WALL


class WeaponType(Enum):
    MINI_BLASTER = (4, 5)
    SCATTER_GUN = (2, 30)
    LASER_RIFLE = (5, 15)
    RAIL_GUN = (10, 10)

    def get_range(self):
        return self.value[0]

    def get_damage(self):
        return self.value[1]


class ShotResult(Enum):
    UNIT_DEAD = -1
    """The unit trying to fire is dead."""

    BLOCKED_BY_WORLD = 0
    """There is a wall between the shooter and target"""

    BLOCKED_BY_OTHER_ENEMY = 1
    """There is another enemy between the shooter and target"""

    HIT_ENEMY = 2
    """The shot hit its mark"""

    TARGET_OUT_OF_RANGE = 3
    """The target was not in range of the shot. Either too far or not in a line"""

    NO_SHOT_ATTEMPTED = 4
    """No shot was attempted"""

    CAN_HIT_ENEMY = 5
    """The shot is preliminarily expected to hit its mark"""

    ENEMY_ALREADY_DEAD = 6
    """The shot was attempted against an already dead enemy"""

    SHOT_INVALID = 7
    """The shot contained invalid data"""

    ENEMY_UNIT_SHIELDED = 8
    """The unit is protected by a shield"""

    FRIENDLY_UNIT_SHIELDED = 9
    """The shooting unit is protected by a shield. Units can't shoot when they are protected by a shield."""



class CallSign(Enum):
    ALPHA = 0
    BRAVO = 1
    CHARLIE = 2
    DELTA = 3


class MoveResult(Enum):
    UNIT_DEAD = -1
    BLOCKED_BY_WORLD = 0
    """The move was blocked by a wall"""

    BLOCKED_BY_FRIENDLY = 1
    """The move was blocked by a unit on the same team"""

    BLOCKED_BY_ENEMY = 2
    """The move was blocked by a unit on the enemy team"""

    NO_MOVE_ATTEMPTED = 3
    """No move was attempted"""

    MOVE_COMPLETED = 4
    """The move was executed successfully"""

    MOVE_VALID = 5
    """The move is preliminarily expected to execute successfully"""

    MOVE_INVALID = 6
    """The move contained invalid data"""



class PickupResult(Enum):
    UNIT_DEAD = -1
    NO_PICK_UP_ATTEMPTED = 0
    """No pick up was attempted"""

    NOTHING_TO_PICK_UP = 1
    """There is nothing to pick up"""

    PICK_UP_VALID = 2
    """The pick-up is preliminarily expected to execute successfully"""

    PICK_UP_COMPLETE = 4
    """The pick-up was executed successfully"""



class ActivateShieldResult(Enum):
    UNIT_DEAD = -1
    NO_SHIELD_ACTIVATION_ATTEMPTED = 0
    """No activation was attempted"""

    NO_SHIELDS_AVAILABLE = 1
    """This unit does not have any shields in its inventory. One must be picked up first."""

    SHIELD_ACTIVATION_VALID = 2
    """The shield is preliminarily expected to activate successfully. It should become active this turn."""

    SHIELD_ACTIVATION_COMPLETE = 3
    """The shield was activated successfully"""



class PickupType(Enum):
    REPAIR_KIT = 0
    SHIELD = 1
    WEAPON_MINI_BLASTER = 2
    WEAPON_SCATTER_GUN = 3
    WEAPON_LASER_RIFLE = 4
    WEAPON_RAIL_GUN = 5


class Team(Enum):
    AMBER = 0
    BLUE = 1
    NONE = -1


class UnitAction(Enum):
    MOVE = 0
    SHOOT = 1
    PICK_UP = 2
    ACTIVATE_SHIELD = 3


class ATZEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        return json.JSONEncoder.default(self, obj)
