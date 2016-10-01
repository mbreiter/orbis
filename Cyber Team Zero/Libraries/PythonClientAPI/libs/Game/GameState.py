class GameState:
    def __init__(self, world, playerUUIDToPlayerTypeMap, playerIndexToUUIDMap, enemyUUID):
        self.world = world
        self.player_uuid_to_player_type_map = playerUUIDToPlayerTypeMap
        self.player_index_to_uuid_map = playerIndexToUUIDMap
        self.enemyUUID = enemyUUID


class SquadTurnActionInfo:
    def __init__(self, unit_actions, unit_action_targets):
        self.unitActions = unit_actions
        self.unitActionTargets = unit_action_targets
