import cProfile
import io
import json
import pstats
import os

import PythonClientAPI.libs.Configurator.Constants as constants
import PythonClientAPI.libs.Communication.CommunicatorConstants as cc
from PythonClientAPI.libs.Game.Entities import *
from PythonClientAPI.libs.Game.Enums import *
from PythonClientAPI.libs.Game.GameState import GameState
from PythonClientAPI.libs.Game.World import World


def parse_config(jsn, player_index):
    dct = json.loads(jsn)
    constants.MAP_NAME = dct["mapName"]
    cc.PORT_NUMBER = int(dct["portNumber"])
    cc.MAXIMUM_ALLOWED_RESPONSE_TIME = int(dct["maxResponseTime"])


def parse_game_state(jsn, tiles):
    dct = json.loads(jsn)
    return as_game_state(dct, tiles)


def parse_tile_data(tile_data):
    dct = json.loads(tile_data)
    return as_tiles(dct["tiles"])


def as_game_state(dct, tiles):
    enemies = []
    friendlies = []
    player_uuid_to_player_type_map = {}
    enemy_uuid = ''
    for uuid in dct['playerUUIDToPlayerTypeMap'].keys():
        units = []

        if uuid == constants.LOCAL_PLAYER_UUID:
            units = as_friendly_unit_list(dct['playerUUIDToPlayerTypeMap'][uuid])
            friendlies = units
        else:
            units = as_enemy_unit_list(dct['playerUUIDToPlayerTypeMap'][uuid])
            enemies = units
            enemy_uuid = uuid

        player_uuid_to_player_type_map[uuid] = units

    player_index_to_uuid_map = {
        index: dct['playerIndexToUUIDMap'][index] for index in dct['playerIndexToUUIDMap'].keys()
        }

    world = as_world(dct['world'], tiles, enemies)

    for friendly in friendlies:
        friendly._world = world
        friendly._enemies = enemies
        friendly._friendlies = friendlies

    return GameState(world, player_uuid_to_player_type_map, player_index_to_uuid_map, enemy_uuid)


def as_point(dct):
    return (dct['x'], dct['y'])


def as_friendly_unit_list(dct):
    return sorted([as_friendly_unit(x) for x in dct], key=lambda unit: unit.call_sign.value)


def as_enemy_unit_list(dct):
    return sorted([as_enemy_unit(x) for x in dct], key=lambda unit: unit.call_sign.value)


def as_enemy_unit(dct):
    return EnemyUnit(as_point(dct['position']), Team[dct['team']], CallSign[dct['callSign']],
                     WeaponType[dct['weaponType']], dct['health'], dct['shieldedTurnsRemaining'], dct['numShields'])


def as_callsign_list(lst):
    return [CallSign[cs] for cs in lst]


def as_friendly_unit(dct):
    """
    :rtype: FriendlyUnit
    """
    return FriendlyUnit(as_point(dct['position']), Team[dct['team']], CallSign[dct['callSign']],
                        WeaponType[dct['weaponType']], dct['health'], dct['shieldedTurnsRemaining'],
                        dct['numShields'], MoveResult[dct['lastMoveResult']],
                        ShotResult[dct['lastShotResult']], PickupResult[dct['lastPickupResult']],
                        ActivateShieldResult[dct['lastShieldActivationResult']],
                        as_callsign_list(dct['lastShooters']),
                        dct['damageTakenLastTurn'],
                        None, None, None)


def as_tiles(dct):
    return [[TileType[tile] for tile in column] for column in dct]


def as_control_point_core(dct, enemies):
    return ControlPoint(as_point(dct['position']), Team[dct['controllingTeam']], dct['name'], dct['isMainframe'],
                        enemies)


def as_control_point_core_list(dct, enemies):
    return [as_control_point_core(cp, enemies) for cp in dct]


def as_pickup(dct):
    return Pickup(as_point(dct['position']), PickupType[dct['type']], dct['pickedUp'])


def as_pickup_list(dct):
    return [as_pickup(cp) for cp in dct]


def as_world(dct, tiles, enemies):
    return World(tiles, dct["width"], dct["height"],
                 as_control_point_core_list(dct["controlPointCores"], enemies), as_pickup_list(dct["pickupCores"]),
                 enemies)
