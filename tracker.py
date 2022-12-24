#/usr/bin/python3

import socket
import pickle

class Tracker:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('localhost', 8000))
        self.sock.listen()
        self.peers = []
        print("tracker initialized")

    def run(self):
        print("listening for peers")
        while True:
            connection , address = self.sock.accept()
            print("new peer connected",address);
            connection.sendall(pickle.dumps(self.peers))
            print("sent peers to:",address)
            peer = pickle.loads(connection.recv(4096))
            self.peers.append(peer)
            print("received peer socket:",peer)
        
tracker = Tracker()
tracker.run()
