import uuid
import json


class Player:
    def __init__(self, name=None) -> None:
        self.uid = str(uuid.uuid4())

        if not name: name = "Jhon Doe"

        self.parameters = {
            'name': name,
            'length': 0,
            'pos_on_road': 0,
            'speed': 0,
            'is_go_left': False,
            'is_go_right': False,
        }
    
    def send_tcp(self, status, data, sock):
        message = json.dumps(
            {
            'success': status,
            'data': data,
            'time': None
            }
        )
        sock.send(message.encode())
    
    def get_parameters(self):
        return self.parameters
    
    def change_pos(self, pos):
        self.game_parameters['position'] = pos
