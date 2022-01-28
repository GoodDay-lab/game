import uuid
from player import Player


ROOM_UPDATE_SEC = 0.05


class Rooms:
    def __init__(self, max_rooms=3) -> None:
        self.max_rooms = max_rooms
        self.players = {
            # uuid: <class Player>
        }
        self.rooms = {
            # rooms: <class Room>
        }
    
    def register(self, request) -> str:
        """ Register player and return a class Player"""
        player = Player()
        self.players[player.uid] = player
        return player

    def create_room(self, user_uid, data) -> str:
        self.check_user_uid(user_uid)

        if len(self.rooms) >= self.max_rooms: raise LimitMaxRooms()

        room = Room(**data)
        self.rooms[room.uid] = room
        player = self.players[user_uid]
        room.join(player)
        return room.uid
    
    def join_room(self, user_uid, room_uid, *data) -> None:
        self.check_user_uid(user_uid)

        player = self.players[user_uid]

        if room_uid is not None:
            self.check_room_uid(room_uid)

            room = self.rooms[room_uid]
            room.join(player)
            return room_uid
        
        elif room_uid is None:
            for room in self.rooms.values():
                if not room.is_full():
                    room.join(player)
                    return room.uid

            room_uid = self.create_room(user_uid)
            self.join_room(user_uid, room_uid=room_uid)
            return room_uid
        
        else:
            raise RoomIsFull()
    
    def leave_room(self, user_uid, room_uid) -> None:
        self.check_user_uid(user_uid)
        self.check_room_uid(room_uid)

        player = self.players[user_uid]
        room = self.rooms[room_uid]

        room.leave(player)
    
    def quit(self, user_uid, room_uid = None) -> None:
        self.check_user_uid(user_uid)
        del self.players[user_uid]
    
    def check_user_uid(self, user_uid):
        if user_uid not in self.players: raise UserNotRegistered()
    
    def check_room_uid(self, room_uid):
        if room_uid not in self.rooms: raise RoomNotRegistered()
    
    def check_user_in_room(self, user_uid, room_uid):
        if self.rooms[room_uid].is_in_room(self.players[user_uid]): raise PlayerNotInRoom()


class Room:
    def __init__(self, max_players=4, name=None) -> None:
        self.uid = str(uuid.uuid4())
        self.players = []
        self.update_count = ROOM_UPDATE_SEC
        self.last_update = 0
        if not name: name = self.uid

        self.settings = {
            'room_uid': self.uid,
            'max_players': max_players,
            'current_players': len(self.players),
            'name': name,
            'is_running': False
        }
    
    def is_full(self) -> bool:
        return len(self.players) == self.settings['max_players']
    
    def is_empty(self) -> bool:
        return len(self.players) == 0
    
    def is_in_room(self, player) -> bool:
        return player in self.players
    
    def join(self, player):
        if self.is_full(): raise RoomIsFull()
        self.players.append(player)
        self.settings['current_players'] += 1
    
    def leave(self, player):
        self.players.remove(player)
        self.settings['current_players'] -= 1

class UserNotRegistered(Exception):
    pass

class RoomNotRegistered(Exception):
    pass

class RoomIsFull(Exception):
    pass

class PlayerNotInRoom(Exception):
    pass

class LimitMaxRooms(Exception):
    pass
