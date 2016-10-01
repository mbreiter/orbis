import cProfile
import io
import json
import pstats
import time

import PythonClientAPI.libs.Communication.CommunicatorConstants as cc
from PythonClientAPI.libs.Communication.ClientChannelHandler import *

# from PythonClientAPI.libs.Game.JSONParser import *
import PythonClientAPI.libs.Game.JSON as JSON
from PythonClientAPI.libs.Communication.AIHandlerThread import *
from PythonClientAPI.libs.Communication.Flag import Flag


class ClientHandlerProtocol():
    def __init__(self, player_ai, port_number, max_response_time, uuidString):
        self.player_ai = player_ai
        self.client_guid = uuidString
        self.game_is_ongoing = False
        self.ai_responded = True
        cc.MAXIMUM_ALLOWED_RESPONSE_TIME = max_response_time
        cc.PORT_NUMBER = port_number
        self.turn = 0
        self.tiles = []

    def start_connection(self):
        self.client_channel_handler = ClientChannelHandler()
        self.client_channel_handler.start_socket_connection(cc.PORT_NUMBER, cc.HOST_NAME)

    def receive_message(self):
        message = ''
        while message == '':
            message = self.client_channel_handler.receive_message()
        return message

    def communication_protocol(self):
        message_from_server = ''
        while (self.game_is_ongoing):
            message_from_server = self.receive_message()
            self.relay_message_and_respond_to(message_from_server)

    def start_communications(self):
        self.start_connection()
        self.game_is_ongoing = True
        self.communication_protocol()

    def end_communications(self):
        self.client_channel_handler.close_connection()
        self.game_is_ongoing = False

    def relay_message_and_respond_to(self, message_from_server):
        if message_from_server == Signals.BEGIN.name:
            self.start_game()
        elif message_from_server == Signals.MOVE.name:
            self.next_move_from_client()
        elif message_from_server == Signals.END.name:
            self.end_communications()
        elif message_from_server == Signals.GET_READY.name:
            # TODO: get world and cache it
            tile_data = self.client_channel_handler.receive_message()
            world_data = self.client_channel_handler.receive_message()
            self.tiles = JSON.parse_tile_data(tile_data)
            self.client_channel_handler.send_message(Signals.READY.name)
        else:
            self.end_communications()
            raise Exception("Unrecognized signal received from server {0}".format(message_from_server))

    def start_game(self):
        self.client_channel_handler.send_message(self.client_guid)

    def next_move_from_client(self):
        # print("=NXTMOV=" * 33)
        # pr = cProfile.Profile()
        # pr.enable()

        game_data_from_server = self.client_channel_handler.receive_message()
        decoded_game_data = JSON.parse_game_state(game_data_from_server, self.tiles)

        client_move = self.get_timed_ai_response(decoded_game_data)
        client_move_json = ""
        if isinstance(client_move, str):
            client_move_json = client_move
        else:
            client_move_json = json.dumps(client_move.__dict__, cls=JSON.ATZEncoder)

        self.client_channel_handler.send_message(client_move_json)

        # self.pprofile(pr)

    def get_timed_ai_response(self, game_data):

        if self.ai_responded:
            self.player_move_event = threading.Event()
            self.ai_handler_thread = AIHandlerThread(kwargs={'player_ai': self.player_ai,
                                                             'decoded_game_data': game_data,
                                                             'player_move_event': self.player_move_event})
            self.ai_handler_thread.start()

        start_time = time.time()
        self.time_response(self.player_move_event, start_time + (cc.MAXIMUM_ALLOWED_RESPONSE_TIME / 1000))
        self.turn += 1
        if self.player_move_event.is_set() and is_valid_response_time(start_time, time.time()):
            self.ai_responded = True
            return self.ai_handler_thread.get_move()
        else:
            print("The AI timed out with a maximum allowed response time of: {0} ms".format(
                cc.MAXIMUM_ALLOWED_RESPONSE_TIME))
            print("time ", (time.time() - start_time) * 1000)
            print("turn ", self.turn)
            self.ai_responded = False

            return Signals.NO_RESPONSE.name

    def pprofile(self, pr):
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue(), file=sys.stderr, flush=True)
        print("=x=" * 33, file=sys.stderr, flush=True)

    def time_response(self, player_move_event, end_time):

        # --------------------------
        # while not player_move_event.is_set() and is_valid_response_time(start_time, time.time()):
        #     time.sleep(0.01)
        while not player_move_event.is_set() and time.time() < end_time:
            player_move_event.wait(0.005)

        # --------------------------e


def is_valid_response_time(start_time, end_time):
    milliseconds_elapsed = (end_time - start_time) * 1000
    return milliseconds_elapsed < cc.MAXIMUM_ALLOWED_RESPONSE_TIME

