import os
import sys
import json
import importlib
import imp

from PythonClientAPI.libs.Communication.ClientHandlerProtocol import *
import PythonClientAPI.libs.Configurator.Constants as constants
import PythonClientAPI.libs.Communication.CommunicatorConstants as cc
from PythonClientAPI.libs.Game.JSON import parse_config
from PythonClientAPI.libs.Navigation.NavigationCache import navigation_cache


class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


if __name__ == '__main__':
    sys.stdout = Unbuffered(sys.stdout)
    sys.stderr = Unbuffered(sys.stderr)
    UUIDForAi = ""

    sys.argv.pop(0)

    cwd = os.getcwd() + "/"
    config_name = ''
    player_index = -1

    for i in range(int(len(sys.argv) / 2)):
        if sys.argv[i * 2] == "-c":
            config_name = sys.argv[i * 2 + 1]
        elif sys.argv[i * 2] == "-d":
            player_index = int(sys.argv[i * 2 + 1])
        elif sys.argv[i * 2] == "-u":
            constants.LOCAL_PLAYER_UUID = sys.argv[i * 2 + 1]
        elif sys.argv[i * 2] == "-cp":
            constants.PLAYER_AI_PATH = sys.argv[i * 2 + 1]

    if player_index == -1:
        if constants.LOCAL_PLAYER_UUID == "Amber":
            player_index = 0
        elif constants.LOCAL_PLAYER_UUID == "Blue":
            player_index = 1
        else:
            print(
                "Player UUID (-u parameter) was neither Amber nor Blue, and the player index (-d parameter) was not specified.")
            sys.exit(0)

    file = open(cwd + 'MatchPresets/' + config_name + ".json", 'r')

    parse_config(file.read(), player_index)

    map_cache_path = cwd + "Maps/" + constants.MAP_NAME + ".nac"

    try:
        sys.path.append(constants.PLAYER_AI_PATH)
        tempString = constants.PLAYER_AI_PATH
        while ('\\' in tempString):
            sys.path.append(tempString[:tempString.rindex('\\')])
            tempString = tempString[:tempString.rindex('\\')]
    except:
        pass
    if map_cache_path == '' or not os.path.isfile(map_cache_path):
        print("Could not find/load map navigation data. Path-finding may be very slow!", file=sys.stderr)
    else:
        navigation_cache.load_compiled_data(map_cache_path)
    UUIDForAi = constants.LOCAL_PLAYER_UUID
    print(constants.PLAYER_AI_PATH)
    print("Welcome " + UUIDForAi)
    fp, pathname, description = imp.find_module('PlayerAI', [constants.PLAYER_AI_PATH])
    player_ai_module = imp.load_module('PlayerAI', fp, pathname, description)
    client_ai = player_ai_module.PlayerAI()
    client_handler_protocol = ClientHandlerProtocol(client_ai, cc.PORT_NUMBER, cc.MAXIMUM_ALLOWED_RESPONSE_TIME,
                                                    UUIDForAi)

    client_handler_protocol.start_communications()
