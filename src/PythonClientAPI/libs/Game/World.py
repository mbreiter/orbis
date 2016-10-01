from collections import deque

from PythonClientAPI.libs.Game.Entities import *
from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Game.PointUtils import MAX_DISTANCE_INT, memoized, are_points_inline, chebyshev_distance
from PythonClientAPI.libs.Navigation.NavigationCache import navigation_cache


class World:
    def __init__(self, tiles, width, height, controlPointCores, pickupCores, enemies):
        """
        :type tiles: list of (list of TileType)
        :type width: int
        :type height: int
        :type controlPointCores: list of ControlPoint
        :type pickupCores: list of Pickup
        :type enemies: list of EnemyUnit
        """
        self._tiles = tiles
        self._enemies = enemies

        self.width = width
        self.height = height
        self.control_points = controlPointCores
        self.pickups = [pickup for pickup in pickupCores if not pickup.pickedUp]

        # Reverse the list if we are on Amber team. This is to enforce symmetry, so that teams on mirrored
        # maps iterate lists in "mirrored" order of each other.
        if self._enemies[0].team == Team.BLUE:
            self.pickups = self.pickups[::-1]
            self.control_points = self.control_points[::-1]
        
        self._pickup_positions_to_pickup_map = {pickup.position: pickup for pickup in self.pickups}
        self._pickup_type_to_position_map = {
            pick_type: [pickup.position for pickup in self.pickups if pickup.pickup_type == pick_type] for pick_type in
            [pickup.pickup_type for pickup in self.pickups]}

    @memoized
    def _can_pass_from_point_in_direction(self, point, direction, block_movement, block_bullets):

        start_tile = self.get_tile(point)

        if not self.is_within_bounds(point):
            return False
        elif (block_movement and start_tile.does_block_movement()) or (
                    block_bullets and start_tile.does_block_bullets()):
            return False

        target = direction.move_point(point)
        target_tile = self.get_tile(target)

        if not self.is_within_bounds(target):
            return False
        elif (block_movement and target_tile.does_block_movement()) or (
                    block_bullets and target_tile.does_block_bullets()):
            return False

        x_part = (target[0], point[1])
        y_part = (point[0], target[1])

        x_part_tile = self.get_tile(x_part)
        y_part_tile = self.get_tile(y_part)

        return not (
            block_movement and x_part_tile.does_block_movement() and y_part_tile.does_block_movement()) and not (
            block_bullets and x_part_tile.does_block_bullets() and y_part_tile.does_block_bullets())

    def _build_path(self, start, destination, tile_to_parent):
        """
        :rtype: (Direction, int)
        """
        step = destination
        direction = Direction.NOWHERE
        length = 0

        while step != start:
            parent = tile_to_parent[step]
            direction = Direction.from_to(parent, step)
            step = parent
            length += 1

        return (direction, length)

    @memoized
    def _get_neighbours(self, current):
        return [
            direction.move_point(current) for direction in
            [Direction.NORTH, Direction.WEST, Direction.SOUTH, Direction.EAST, Direction.NORTH_WEST,
             Direction.SOUTH_WEST, Direction.SOUTH_EAST, Direction.NORTH_EAST]
            if self._can_pass_from_point_in_direction(current, direction, True, False)
            ]

    def _ray_cast_distance(self, source, direction, block_movement, block_bullets, max_distance=MAX_DISTANCE_INT):
        if direction == Direction.NOWHERE or max_distance <= 0:
            return 0

        distance = 0
        current = source
        while distance < max_distance and self._can_pass_from_point_in_direction(current, direction, block_movement,
                                                                                 block_bullets):
            distance += 1
            current = direction.move_point(current)

        return distance

    @memoized
    def _get_next_direction_in_path_and_length(self, start, destination, calc_length=False):

        if not self.is_within_bounds(start) or not self.is_within_bounds(destination) or \
                self.get_tile(start).does_block_movement() or \
                self.get_tile(destination).does_block_movement() or \
                start == destination:
            return (Direction.NOWHERE, 0)

        if navigation_cache.loaded:
            length = 0
            if calc_length:
                current = (start[0], start[1])
                while current != destination:
                    direction = navigation_cache.get_next_direction_in_path(current, destination)
                    if direction == Direction.NOWHERE:
                        length = 0
                        break
                    current = direction.move_point(current)
                    length += 1

            return (navigation_cache.get_next_direction_in_path(start, destination), length)

        tile_to_parent = {start: None}
        search_q = deque(maxlen=self.width * self.height)

        search_q.append(start)
        q_len = 1

        found = False

        while not found and q_len > 0:
            current = search_q.popleft()
            q_len -= 1
            for neighbour in self._get_neighbours(current):
                if neighbour not in tile_to_parent:
                    search_q.append(neighbour)
                    q_len += 1
                    tile_to_parent[neighbour] = current

                if neighbour == destination:
                    found = True
                    break

        if not found:
            return (Direction.NOWHERE, 0)

        return self._build_path(start, destination, tile_to_parent)

    def get_pickup_at_position(self, position):
        """
        Returns the pickup located at the given coordinates, or None if there is no pickup there.

        :param (int,int) position: The coordinates to check
        :rtype: PickupType
        """
        return self._pickup_positions_to_pickup_map.get(position)

    def get_positions_of_pickup_type(self, pickup_type):
        """
        Returns all the coordinates of the map that contain a Pickup of the given PickupType
        Returns an empty list if there is no such pickup on the field.

        :param PickupType pickup_type: The type of pickup to look for.
        :rtype: list of (int,int)
        """
        positions = self._pickup_type_to_position_map.get(pickup_type, [])
        
        # Reverse the list if we are on Amber team. This is to enforce symmetry, so that teams on mirrored
        # maps iterate lists in "mirrored" order of each other.
        if self._enemies[0].team == Team.BLUE:
            positions = positions[::-1]
        return positions

    def get_tile(self, point):
        """
        Returns the TileType at the given point

        :param (int,int) point: The point to check
        :rtype: TileType
        """
        if not self.is_within_bounds(point):
            return None
        return self._tiles[point[0]][point[1]]

    @memoized
    def is_within_bounds(self, point):
        """
        Checks if the given point is within the world bounds

        :param (int,int) point: The point to check
        :rtype: bool
        """
        return 0 <= point[0] < self.width and 0 <= point[1] < self.height

    def can_move_from_point_in_direction(self, start, direction):
        """
        Returns true iff something located at point start could possibly move in the given direction

        :param (int,int) start: The point to start at
        :param Direction direction: The direction in which to check the move
        :rtype: bool
        """
        return self._can_pass_from_point_in_direction(start, direction, True, False)

    def get_next_direction_in_path(self, start, destination):
        """
        Gets the next direction in the shortest path from the given start tile to the given destination.
        Avoids walls, but not units. This function will run extremely quickly if the map has a navigation cache
        (.nac) file. All maps provided in the game and tournament will have this file. Check the manual for
        instructions on generating the files for your own custom maps.

        :param (int,int) start: The tile to start path finding from
        :param (int,int) destination: The tile to try to find a path to
        :rtype: Direction
        :return: The direction to move in from the start tile to get to the destination tile. Returns NOWHERE if there
            is no way to get to the destination or if the start tile is the same as the destination (you are already there).
        """
        return self._get_next_direction_in_path_and_length(start, destination)[0]

    def get_path_length(self, start, destination):
        """
        Calculates the length of the shortest path from the starting point to the end point.

        :return: 0 if the path does not exist or if the start and end points are the same, otherwise the length
            of the path (in tiles).
        :param (int,int) start: The point to start the path at
        :param (int,int) destination: The point to end the path at
        :rtype: int
        """
        return self._get_next_direction_in_path_and_length(start, destination, True)[1]

    def can_shooter_shoot_target(self, shooter_pos, target_pos, max_distance=MAX_DISTANCE_INT):
        """
        Returns true iff there is a clear line of fire from shooter to
        target. This takes walls into account.

        :param (int,int) shooter_pos: The source of the shot
        :param (int,int) target_pos: The target of the shot
        :param int max_distance: Maximum distance in tiles that the bullet can travel
        """
        if shooter_pos == target_pos or max_distance <= 0 \
                or not self.is_within_bounds(shooter_pos) or not self.is_within_bounds(target_pos) \
                or not are_points_inline(shooter_pos, target_pos) \
                or self.get_tile(shooter_pos).does_block_movement() or self.get_tile(target_pos).does_block_movement():
            return False

        shot_direction = Direction.from_to(shooter_pos, target_pos)

        distance = chebyshev_distance(shooter_pos, target_pos)

        return max_distance >= distance == self._ray_cast_distance(shooter_pos, shot_direction, False, True, distance)

    def get_closest_shootable_enemy_in_direction(self, shooter, direction):
        """
        Finds the closest :class:`EnemyUnit` in the given :class:`Direction` that can be shot by the given :class:`FriendlyUnit`.
        Takes into account walls, and the FriendlyUnit's shot range.

        :param FriendlyUnit shooter: The unit firing the shot
        :param Direction direction: The direction to look in
        :return: The closest :class:`EnemyUnit` that the :class:`FriendlyUnit` can shoot, or None if no
            enemy can be shot in that direction.

        :rtype: EnemyUnit
        """
        if direction is None or direction == Direction.NOWHERE or shooter is None or shooter.health <= 0:
            return None

        def get_distance_to_shooter(enemy):
            if enemy.health <= 0 or direction.from_to(shooter.position, enemy.position) != direction:
                return MAX_DISTANCE_INT

            distance = chebyshev_distance(shooter.position, enemy.position)

            if not self.can_shooter_shoot_target(shooter.position, enemy.position,
                                                 shooter.current_weapon_type.get_range()):
                return MAX_DISTANCE_INT

            return distance

        closest = min(self._enemies, key=get_distance_to_shooter)

        if get_distance_to_shooter(closest) > shooter.current_weapon_type.get_range():
            return None

        return closest

    def get_nearest_control_point(self, position):
        """Find and return the control point with the closest linear distance (i.e. ignoring any obstacles/walls;
        "as the crow flies") to the given point. If no control points on the map, returns None.

        :param position: The Point to look from
        """
        if len(self.control_points) == 0:
            return None

        return min(self.control_points,
                   key=lambda control_point: chebyshev_distance(control_point.position, position))
