import socket
import json
import threading
import os

import socket
import threading
import time
import uuid
from threading import Thread
from statuses import *


class AuthorizationService():
    def __init__(self, sender):
        self.is_running = True
        self.query = []
        self.sender = sender
        self.thread = Thread(target=self.run)
        self.thread.start()

    def authorize(self, client, request):
        self.query.append((client, request))

    def run(self):
        while self.is_running:
            if not len(self.query):
                continue
            client, request = self.query.pop(0)
            response = self.parse_request(request)
            self.send_response(client, response)

    def send_response(self, client, response):
        self.sender.send(client, response)

    def parse_request(self, request):
        try:
            login, password = request['login'], request['password']
        except KeyError:
            return self.create_response(FAILED_AUTH, "WRONG REQUEST")
        return self.create_response(SUCCESS_AUTH, str(uuid.uuid4()))

    def create_response(self, status, message):
        response = {
            "status": status,
            "message": message
        }
        return response


class SenderService():
    def __init__(self):
        self.is_running = True
        self.query = []
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        while self.is_running:
            if not len(self.query):
                continue
            client, response = self.query.pop(0)
            client.send(response)
            client.close()

    def send(self, client, response):
        response = json.dumps(response).encode()
        self.query.append((client, response))


sendService = SenderService()
authService = AuthorizationService(sendService)

def main(tcp_host, tcp_port):
    servSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servSock.settimeout(1)
    servSock.setblocking(1)
    servSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servSock.bind((tcp_host, tcp_port))
    servSock.listen(10)

    is_running = True

    while is_running:
        try:
            client, addr = servSock.accept()
        except socket.timeout:
            continue

        request = json.loads(client.recv(2048))

        if request['action'] == 'AUTH':
            authService.authorize(client, request)


if __name__ == '__main__':
    main('0.0.0.0', 5555)
