import socket
import json
from threading import Thread, Lock
from rooms import *
import sys
import time


THREADS = []
players = {}


def main_loop(tcp_host, tcp_port, room_manager):
    is_running = True
    lock = Lock()

    print('+-------------------------------+')
    print(f'| HOST: {tcp_host}               |')
    print(f'| PORT: {tcp_port}                    |')
    print(f'+-------------------------------+')
    print('| ENTER COMMAND TO:             |')
    print('| rooms - return all rooms      |')
    print('| players - return all players  |')
    print('| quit - correctly ends server  |')
    print('+-------------------------------+')

    tcp_listenner = TcpListenner(tcp_host, tcp_port, lock, room_manager)
    tcp_listenner.start()

    while is_running:
        cmd = input('| admin@admin [~] $ ')

        if cmd == 'quit':
            print('| wait...')
            tcp_listenner.is_running = False
            is_running = False
        
        if cmd == 'players':
            list_players = room_manager.players.values()
            print()
            print(f'+{"-" * 60}+')
            print(f'| PLAYERS FOUND {len(list_players)}')

            for player in list_players:
                print(f'+{"-" * 60}+')
                print(f'| NAME: {player.parameters["name"]}')
                print(f'| UID: {player.uid}')
                print(f'| DATA:')
                for key in player.parameters:
                    print(f'|\t{key.upper()} - {player.parameters[key]}')
            print(f'+{"-" * 60}+')
            print()
        
        if cmd == 'rooms':
            list_rooms = room_manager.rooms.values()
            print()
            print(f'+{"-" * 60}+')
            print(f'| ROOMS FOUND {len(list_rooms)}')

            for room in list_rooms:
                print(f'+{"-" * 60}+')
                print(f'| NAME: {room.settings["name"]}')
                print(f'| UID: {room.settings["room_uid"]}')
                print(f'| PLAYERS: {room.settings["current_players"]}/{room.settings["max_players"]}')
                for player in room.players:
                    print(f'|\tNAME: {player.parameters["name"]}')
                    print(f'|\tUID: {player.uid}')
            print(f'+{"-" * 60}+')
            print()
    
    tcp_listenner.join()


def rooms_update(rooms: dict, players: dict):
    i = 0
    while True:
        if len(rooms) > 0:
            i = i % len(rooms)
            room = list(rooms.values())[i]
            param = time.time() - room.last_update >= room.update_count * 0.1
            room.last_update = time.time()
            for player in room.players:
                if player not in players.values():
                    room.leave(player)
                else:
                    if param:
                        player.parameters['length'] += player.parameters['speed'] * 0.1
            i += 1
        yield


class TcpListenner(Thread):
    def __init__(self, host, port, lock, room_manager):
        Thread.__init__(self)
        self.address = (host, port)
        self.lock = lock
        self.is_running = True
        self.room_manager = room_manager
    
    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(self.address)
        self.sock.setblocking(0)
        self.sock.settimeout(5)
        self.sock.listen(5)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        updater = rooms_update(self.room_manager.rooms, self.room_manager.players)

        while self.is_running:
            next(updater)
            try:
                client, addr = self.sock.accept()
            except socket.timeout:
                continue

            request = client.recv(1024)
            self.lock.acquire()
            try:
                data = json.loads(request)
                self.route(data, client, addr)
            except (RoomNotRegistered, RoomIsFull, PlayerNotInRoom, LimitMaxRooms) as error:
                player = self.room_manager.players[data['user_uid']]
                player.send_tcp(False, {'Error': error.__dict__}, client)
            except UserNotRegistered:
                pass
            except json.decoder.JSONDecodeError:
                pass
            except Exception as error:
                print(error)
            finally:
                self.lock.release()
            client.close()
        self.sock.close()
    
    def route(self, data, client, addr):
        action = data['action']

        if action == 'register':
            player = self.room_manager.register(data)
            message = {'user_uid': player.uid, 'start_stats': player.get_parameters()}
            player.send_tcp(True, message, client)
            return

        if action == 'send_data':
            self.room_manager.check_user_uid(data['user_uid'])
            player = self.room_manager.players[data['user_uid']]
            manage_data(player, data['data'])
            return
        
        if action == 'get_data':
            self.room_manager.check_user_uid(data['user_uid'])
            self.room_manager.check_room_uid(data['room_uid'])
            room = self.room_manager.rooms[data['room_uid']]
            message = [player.get_parameters() for player in sorted(room.players,
                                                                    key=lambda player: player.uid != data['user_uid'])]
            player = self.room_manager.players[data['user_uid']]
            player.send_tcp(True, message, client)
            return
        
        if action == 'create_room':
            self.room_manager.check_user_uid(data['user_uid'])
            room_uid = self.room_manager.create_room(data['user_uid'], data['settings'])
            player = self.room_manager.players[data['user_uid']]
            message = {'room_uid': room_uid}
            player.send_tcp(True, message, client)
            return
        
        if action == 'join_room':
            self.room_manager.check_user_uid(data['user_uid'])
            room_uid = self.room_manager.join_room(data['user_uid'], data['room_uid'])
            player = self.room_manager.players[data['user_uid']]
            message = {'room_uid': room_uid}
            player.send_tcp(True, message, client)
            return
        
        if action == 'leave_room':
            self.room_manager.check_user_uid(data['user_uid'])
            self.room_manager.leave_room(data['user_uid'], data['room_uid'])
            player = self.room_manager.players[data['user_uid']]
            return
        
        if action == 'get_rooms':
            self.room_manager.check_user_uid(data['user_uid'])
            player = self.room_manager.players[data['user_uid']]
            message = {'rooms': [room.settings for room in self.room_manager.rooms.values()]}
            player.send_tcp(True, message, client)
            return
        
        if action == 'set_name':
            self.room_manager.check_user_uid(data['user_uid'])
            player = self.room_manager.players[data['user_uid']]
            player.parameters['name'] = data['name']
            return
         
        if action == 'quit':
            self.room_manager.check_user_uid(data['user_uid'])
            self.room_manager.quit(data['user_uid'])
            return


def manage_data(player, data):
    speed = player.parameters['speed']
    player.parameters['speed'] = max(min(speed + data['up'] * 0.02 - data['down'] * 0.02 - 0.01 * (speed > 0), 127), -34)
    player.parameters['speed'] = round(player.parameters['speed'], 5)
    player.parameters['pos_on_road'] = max(min(player.parameters['pos_on_road'] + -0.02 * data['left'] + 0.02 * data['right'], 1), -1)
    player.parameters['is_go_left'] = data['left']
    player.parameters['is_go_right'] = data['right']


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        main_loop(sys.argv[1], int(sys.argv[2]), Rooms(100))
    else:
        print('Select host and port')
