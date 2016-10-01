from PythonClientAPI.libs.Game import PointUtils
from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Game.PointUtils import chebyshev_distance
from PythonClientAPI.libs.Game.Weapon import ProjectileWeapon
from PythonClientAPI.libs.Game.World import World


class Entity:
    """ A general game object with x and y coordinates representing its location on the gameboard.

    Attributes:
        position (int,int): Represents the x and y-coordinate on the gameboard.
    """

    def __init__(self, position):
        self.position = position

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.position == other.position)

    def __ne__(self, other):
        return not self.__eq__(other)


class Unit(Entity):
    """ A general object representing a unit

    Inherits from Entity.

    Attributes:
        team (Team): Unit team
        call_sign (CallSign): Unit call sign
        health (int): Unit health
        current_weapon_type (WeaponType): The current weapon the unit has equipped
    """

    def __init__(self, position, team, call_sign, weaponType, health, shieldedTurnsRemaining, numShields):
        """
        :type position: (int,int)
        :type team: Team
        :type call_sign: CallSign
        :type weaponType: WeaponType
        :type health: int
        :type shieldedTurnsRemaining: int
        :type numShields: int
        """
        super().__init__(position)
        self.team = team
        self.call_sign = call_sign
        self.health = health
        self.current_weapon_type = weaponType
        self.shielded_turns_remaining = shieldedTurnsRemaining
        self.num_shields = numShields

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.team == other.team and self.call_sign == other.call_sign

    def __hash__(self):
        return self.call_sign.value * 31 + self.team.value

    def __repr__(self):
        return self.call_sign.name


class FriendlyUnit(Unit):
    """
    This class represents a unit your AI can control.
    """

    def __init__(self, position, team, call_sign, weaponType, health, shieldedTurnsRemaining, numShields,
                 lastMoveResult, lastShotResult, lastPickupResult, lastShieldActivationResult,
                 lastShooters, damageTakenLastTurn, world, enemies, friendlies):
        """
        :type position: (int,int)
        :type team: Team
        :type call_sign: CallSign
        :type weaponType: WeaponType
        :type health: int
        :type lastMoveResult: MoveResult
        :type lastShotResult: ShotResult
        :type lastPickupResult: PickupResult
        :type lastShieldActivationResult: ActivateShieldResult
        :type lastShooters: list of EnemyUnit
        :type damageTakenLastTurn: int
        :type world: World
        :type enemies: list of EnemyUnit
        :type friendlies: list of FriendlyUnit
        :type shieldedTurnsRemaining: int
        :type numShields: int
        """
        super().__init__(position, team, call_sign, weaponType, health, shieldedTurnsRemaining, numShields)
        self._last_shooters = lastShooters
        self._world = world
        self._enemies = enemies
        self._friendlies = friendlies
        self._next_action = None
        self._next_action_target = None

        self.last_move_result = lastMoveResult
        self.last_shot_result = lastShotResult
        self.last_pickup_result = lastPickupResult
        self.last_shield_activation_result = lastShieldActivationResult
        self.damage_taken_last_turn = damageTakenLastTurn
        self.last_action_succeeded = \
            (self.last_move_result == MoveResult.NO_MOVE_ATTEMPTED or self.last_move_result == MoveResult.MOVE_COMPLETED) and \
            (self.last_shot_result == ShotResult.NO_SHOT_ATTEMPTED or self.last_shot_result == ShotResult.HIT_ENEMY) and \
            (self.last_pickup_result == PickupResult.NO_PICK_UP_ATTEMPTED or self.last_pickup_result == PickupResult.PICK_UP_COMPLETE) and \
            (self.last_shield_activation_result == ActivateShieldResult.NO_SHIELD_ACTIVATION_ATTEMPTED or self.last_shield_activation_result == ActivateShieldResult.SHIELD_ACTIVATION_COMPLETE)

    def shoot_at(self, enemy_unit):
        """
        Orders this Unit to fire its weapon at the given enemy unit at the end of this turn.
        Note that damage will not be applied until the turn is over.

        :param EnemyUnit enemy_unit: The enemy unit to shoot at.
        :return: The expected result of trying to shoot the enemy.
        :rtype: ShotResult
        """
        check = self.check_shot_against_enemy(enemy_unit)

        if check == ShotResult.CAN_HIT_ENEMY:
            self._next_action = UnitAction.SHOOT
            self._next_action_target = enemy_unit.position

        return check

    def move(self, direction):
        """
        Orders this Unit to move one tile in the given direction at the end of this turn.
        Note that the unit will not move until the turn is over.

        :param Direction direction: The direction to move in

        :return: The result of attempting to make this move. If this is MOVE_VALID, this does not guarantee
            the move will succeed. The move will succeed ONLY if no enemy or friendly stays in, or attempts to move
            to the tile in the given Direction. Thus you won't know the final result of the move until the current turn completes.
            You can find out the result of the move from the previous turn from :meth:`FriendlyUnit.getLastMoveResult`.

        :rtype: MoveResult
        """
        check = self.check_move_in_direction(direction)

        if check == MoveResult.MOVE_VALID:
            self._next_action = UnitAction.MOVE
            self._next_action_target = direction.move_point(self.position)

        return check

    def move_to_destination(self, destination):
        """
        Orders this unit to move one tile towards the given destination. This will use the built in
        path-finding system to find the next move along the shortest path.

        :param (int,int) destination: The point to move towards.

        :return: The result of attempting to make this move. If this is MOVE_VALID, this does not guarantee
            the move will succeed. The move will succeed ONLY if no enemy or friendly stays in, or attempts to move
            to the tile in the given Direction. Thus you won't know the final result of the move until the current turn completes.
            You can find out the result of the move from the previous turn from :meth:`FriendlyUnit.getLastMoveResult`.

        :rtype: MoveResult
        """
        direction = self._world.get_next_direction_in_path(self.position, destination)
        return self.move(direction)

    def check_shot_against_enemy(self, enemy):
        """
        Checks the expected result if this unit tries to shoot the given enemy unit with
        :meth:`shoot_at`

        :param EnemyUnit enemy: The enemy unit to try to check the shot against.
        :return: The expected result if you tried to shoot this enemy unit.
        :rtype: ShotResult
        """
        if self.health <= 0:
            return ShotResult.UNIT_DEAD

        return ProjectileWeapon.check_shot_against_enemy(self, enemy, self._world, self.current_weapon_type)

    def check_move_to_destination(self, destination):
        """
        Checks whether this unit can move one tile on the path to the given Point. This will use the built in
        path-finding system to find the next move along the shortest path.
        Does not actually move the unit. This check does not take into account the positions
        of friendly and enemy units as they might change by the time the move is actually performed.

        :param (int,int) destination: The point to move towards.
        :rtype: MoveResult
        :return: The expected result if you were to try to move. If this is NO_MOVE_ATTEMPTED, then a path could not be
            found to the destination point.

        """
        direction = self._world.get_next_direction_in_path(self.position, destination)
        return self.check_move_in_direction(direction)

    def check_move_in_direction(self, direction):
        """
        Checks whether this unit can move one tile in the given direction.
        Does not actually move the unit. This check does not take into account the positions
        of friendly and enemy units as they might change by the time the move is actually performed.

        :type direction: Direction
        :param direction: The direction to check.
        :return: The expected result if you were to try to move.
        :rtype: MoveResult
        """
        if self.health <= 0:
            return MoveResult.UNIT_DEAD
        elif direction is None or direction == Direction.NOWHERE:
            return MoveResult.NO_MOVE_ATTEMPTED
        elif not self._world.can_move_from_point_in_direction(self.position, direction):
            return MoveResult.BLOCKED_BY_WORLD
        elif self._will_be_blocked_by_friendly(direction):
            return MoveResult.BLOCKED_BY_FRIENDLY
        else:
            return MoveResult.MOVE_VALID

    def _will_be_blocked_by_friendly(self, move_dir):
        target = move_dir.move_point(self.position)
        for friendly in self._friendlies:
            if friendly == self:
                continue
            if (target == friendly.position and
                    (friendly._next_action == UnitAction.SHOOT or friendly._next_action == UnitAction.PICK_UP)) or \
                    (target == friendly._next_action_target and friendly._next_action == UnitAction.MOVE):
                return True
        return False

    def get_last_turn_shooters(self):
        """
        Returns a list of EnemyUnits that shot this FriendlyUnit last turn.
        Can be an empty array of nobody shot this FriendlyUnit.

        :rtype: list of EnemyUnit
        """
        shooters = []
        for enemy in self._enemies:
            if enemy.call_sign in self._last_shooters:
                shooters.append(enemy)
        return shooters

    def check_pickup_result(self):
        """
        Checks if there is a pickup item at this unit's position

        :rtype: PickupResult
        :return: PickupResult.PICK_UP_VALID if there is a pickup, or PickupResult.NOTHING_TO_PICK_UP if there isn't.
            Note, you can find the exact type of pickup by getting a reference to it with :func:`World.get_pickup_at_position`
        """
        if self.health <= 0:
            return PickupResult.UNIT_DEAD
        return PickupResult.NOTHING_TO_PICK_UP if self._world.get_pickup_at_position(
            self.position) is None else PickupResult.PICK_UP_VALID

    def pickup_item_at_position(self):
        """
        Tries to pickup the pickup item at this unit's position. If there is an item, then picking it up will be
        this unit's action for the next turn.

        :return: PickupResult.PICK_UP_VALID if there is a pickup, or PickupResult.NOTHING_TO_PICK_UP if there isn't.
            Note, you can find the exact type of pickup by getting a reference to it with :func:`World.get_pickup_at_position`
        :rtype: PickupResult
        """
        can_pickup_result = self.check_pickup_result()
        if can_pickup_result != PickupResult.PICK_UP_VALID:
            return can_pickup_result

        self._next_action = UnitAction.PICK_UP
        self._next_action_target = self.position

        return PickupResult.PICK_UP_VALID

    def check_shield_activation(self):
        """
        Check the result of trying to activate a shield.

        :rtype: ActivateShieldResult

        :return: If the unit is dead, returns ActivateShieldResult.UNIT_DEAD,
            if the unit has no shields, returns ActivateShieldResult.NO_SHIELDS_AVAILABLE,
            otherwise returns ActivateShieldResult.SHIELD_ACTIVATION_VALID.
        """
        if self.health <= 0:
            return ActivateShieldResult.UNIT_DEAD
        elif self.num_shields <= 0:
            return ActivateShieldResult.NO_SHIELDS_AVAILABLE
        else:
            return ActivateShieldResult.SHIELD_ACTIVATION_VALID

    def activate_shield(self):
        """
        Orders the unit to activate a shield this turn.

        :rtype: ActivateShieldResult

        :return: If the unit is dead, returns ActivateShieldResult.UNIT_DEAD,
            if the unit has no shields, returns ActivateShieldResult.NO_SHIELDS_AVAILABLE,
            otherwise returns ActivateShieldResult.SHIELD_ACTIVATION_VALID.
        """
        check_result = self.check_shield_activation()
        if check_result != ActivateShieldResult.SHIELD_ACTIVATION_VALID:
            return check_result

        self._next_action = UnitAction.ACTIVATE_SHIELD
        self._next_action_target = self.position

        return ActivateShieldResult.SHIELD_ACTIVATION_VALID

    def standby(self):
        """
        Orders this unit to do nothing and stay in place this turn.
        """
        self._next_action = None
        self._next_action_target = None


class EnemyUnit(Unit):
    def __init__(self, position, team, call_sign, weaponType, health, shieldedTurnsRemaining, numShields):
        """
        :type position: (int,int)
        :type team: Team
        :type call_sign: CallSign
        :type weaponType: WeaponType
        :type health: int
        :type shieldedTurnsRemaining: int
        :type numShields: int
        """
        super().__init__(position, team, call_sign, weaponType, health, shieldedTurnsRemaining, numShields)


class ControlPoint(Entity):
    def __init__(self, position, controllingTeam, name, enemies, isMainframe):
        """
        :type position: (int,int)
        :type controllingTeam: Team
        :type name: str
        :type enemies: list of EnemyUnit
        """
        super().__init__(position)
        self._enemies = enemies

        self.controlling_team = controllingTeam
        self.name = name
        self.is_mainframe = isMainframe

    def get_num_enemy_units_around(self):
        """
        Returns the number of enemy units that are on tiles adjacent to or on this control point.
        """
        return len([enemy for enemy in self._enemies if
                    (enemy.health > 0 and chebyshev_distance(enemy.position, self.position) <= 1)])


class Pickup(Entity):
    def __init__(self, position, type, pickedUp):
        """
        :type position: (int,int)
        :type type: PickupType
        :type pickedUp: bool
        """
        super().__init__(position)
        self.pickup_type = type
        self.pickedUp = pickedUp

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.position == other.position and self.pickup_type == other.type

    def __ne__(self, other):
        return not self.__eq__(other)
