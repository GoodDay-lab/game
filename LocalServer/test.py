import socket
import json
import time


def p():
    time1 = time.time()
    i = 0
    while True:
        if not (i % 4):
            print('--- ', time.time() - time1)
            time1 = time.time()
            i = 0
        i += 1
        yield

er = p()
while True:
    next(er)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 5555))
    t = time.time()
    sock.send(json.dumps({'action': 'AUTH', 'login': '123', 'password': '32'}).encode())
    sock.recv(1024)
    time.sleep(1/100)