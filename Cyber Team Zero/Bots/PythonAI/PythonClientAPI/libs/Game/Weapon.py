from PythonClientAPI.libs.Game import PointUtils
from PythonClientAPI.libs.Game.Enums import ShotResult, Direction
from PythonClientAPI.libs.Game.Entities import *
from PythonClientAPI.libs.Game.World import World


class ProjectileWeapon:
    """
    Utility class for performing shot checks.
    """
    @staticmethod
    def check_shot_against_point(shooter, target_point, world, weapon_type):
        """
        Checks if the given shooter would be able to hit the given target point with the given weapon
        :param Unit shooter: The shooting unit
        :param (int,int) target_point: The point the shooter is trying to hit
        :param World world: The world
        :param WeaponType weapon_type: The WeaponType to test with
        :return: A ShotResult indicated the expected outcome of the shot.
        :rtype: ShotResult
        """
        if PointUtils.chebyshev_distance(shooter.position, target_point) > weapon_type.get_range() or \
                not PointUtils.are_points_inline(shooter.position, target_point):
            return ShotResult.TARGET_OUT_OF_RANGE
        elif not world.can_shooter_shoot_target(shooter.position, target_point, weapon_type.get_range()):
            return ShotResult.BLOCKED_BY_WORLD
        return ShotResult.CAN_HIT_ENEMY

    @staticmethod
    def check_shot_against_enemy(shooter, target_enemy, world, weapon_type):
        """
        Checks if the given shooter would be able to hit the given target enemy with the given weapon
        :param FriendlyUnit shooter: The shooting unit
        :param EnemyUnit target_enemy: The enemy the shooter is trying to hit
        :param World world: The world
        :param WeaponType weapon_type: The WeaponType to test with
        :return: A ShotResult indicated the expected outcome of the shot.
        :rtype: ShotResult
        """
        if target_enemy is None:
            return ShotResult.NO_SHOT_ATTEMPTED
        elif target_enemy.health <= 0:
            return ShotResult.ENEMY_ALREADY_DEAD
        elif shooter.shielded_turns_remaining > 0:
            return ShotResult.FRIENDLY_UNIT_SHIELDED
        elif target_enemy.shielded_turns_remaining > 0:
            return ShotResult.ENEMY_UNIT_SHIELDED

        point_check = ProjectileWeapon.check_shot_against_point(shooter, target_enemy.position, world, weapon_type)
        if point_check == ShotResult.CAN_HIT_ENEMY:
            if world.get_closest_shootable_enemy_in_direction(shooter, Direction.from_to(shooter.position, target_enemy.position)) != target_enemy:
                return ShotResult.BLOCKED_BY_OTHER_ENEMY
        else:
            return point_check
        return ShotResult.CAN_HIT_ENEMY


