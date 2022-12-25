#/usr/bin/python3

import socket
import threading
import pickle
import sys
import uuid


class Peer:
    def __init__(self, tracker_address, tracker_port):
        # Initialize Peer
        self.peers = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('localhost', 0))
        self.sock.listen()
        self.address = uuid.uuid4().hex
        print("socket initialized",self.address)

        # Connect to Tracker
        self.tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tracker.connect((tracker_address, tracker_port))
        print("connected to tracker")
        peers = pickle.loads(self.tracker.recv(4096))
        print(f'peers: {peers}')

        # Send Peer Socket to Tracker
        self.tracker.send(pickle.dumps({self.sock.getsockname()}))

        # listen for connections
        accept_thread = threading.Thread(target=self.accept_peers,args=())
        accept_thread.start()

        # connect to peers
        for peer in peers:
            self.connect_peer(peer)

        while True:
            message = sys.stdin.readline().strip()
            for peer in self.peers:
                peer.send(message.encode())

    def accept_peers(self):
        while True:
            peer_socket, peer_address = self.sock.accept()
            print(f'peer connected: {peer_address}')
            self.peers.append(peer_socket)
            self.receive_peer(peer_socket)

    def connect_peer(self,peer):
        try:
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sock.connect(peer)
            print("connected to peer:",peer)
            self.peers.append(pickle.loads(sock.recv(4096)))
            self.receive_peer(sock)
        except:
            print("connection failed:",peer)

    def receive_peer(self,sock):
        # receive from peers
        def receive():
            while True:
                message = sock.recv(4096)
                if not message:
                    sock.close()
                    break
                print("received:",message.decode())
        receive_thread = threading.Thread(target=receive,args=())
        receive_thread.start()


# Create a peer
peer = Peer("localhost", 8000)
