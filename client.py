import socket
import json
import time

class Client:
    def __init__(self, server_host, server_port) -> None:
        self.server_address = (server_host, server_port)
        self.user_uid = None
        self.room_uid = None
        self.server_message = []
        self.register()
    
    def send_message(self, message):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.server_address)
        self.sock.send(json.dumps(message).encode())
    
    def register(self):
        message = {
            'action': 'register',
        }
        self.send_message(message)
        response = json.loads(self.sock.recv(1024))
        response = self.parse_response(response)
        self.user_uid = response['user_uid']
        return response['start_stats']
    
    def send_data(self, data):
        message = {
            'action': 'send_data',
            'user_uid': self.user_uid,
            'data': data
        }
        self.send_message(message)
    
    def get_data(self):
        message = {
            'action': 'get_data',
            'user_uid': self.user_uid,
            'room_uid': self.room_uid
        }
        self.send_message(message)
        response = json.loads(self.sock.recv(2048))
        response = self.parse_response(response)
        return response
    
    def quit(self):
        message = {
            'action': 'quit',
            'user_uid': self.user_uid
        }
        self.send_message(message)
    
    def create_room(self, **settings):
        message = {
            'action': 'create_room',
            'user_uid': self.user_uid,
            'settings': settings
        }
        self.send_message(message)
        response = json.loads(self.sock.recv(1024))
        response = self.parse_response(response)
        self.room_uid = response['room_uid']
    
    def join_room(self, room_uid=None):
        message = {
            'action': 'join_room',
            'user_uid': self.user_uid,
            'room_uid': room_uid
        }
        self.send_message(message)
        response = json.loads(self.sock.recv(1024))
        response = self.parse_response(response)
        self.room_uid = response['room_uid']
    
    def leave_room(self):
        message = {
            'action': 'leave_room',
            'user_uid': self.user_uid,
            'room_uid': self.room_uid
        }
        self.send_message(message)
        self.room_uid = None
    
    def get_rooms(self):
        message = {
            'action': 'get_rooms',
            'user_uid': self.user_uid
        }
        self.send_message(message)
        response = json.loads(self.sock.recv(4096))
        response = self.parse_response(response)
        print(response)
        return response['rooms']
    
    def set_name(self, name):
        message = {
            'action': 'set_name',
            'user_uid': self.user_uid,
            'name': name
        }
        self.send_message(message)
    
    def parse_response(self, response):
        if response['success']:
            return response['data']
        else:
            print(response['data'])
            raise Exception()


if __name__ == '__main__':
    pass
