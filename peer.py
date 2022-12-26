#/usr/bin/python3

import socket
import threading
import pickle
import sys
import uuid
import datetime



class Peer:
    def __init__(self, tracker_address, tracker_port):
        # Initialize Peer
        self.peers = {}

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
        self.tracker.send(pickle.dumps(self.sock.getsockname()))

        # listen for connections
        accept_thread = threading.Thread(target=self.accept_peers,args=())
        accept_thread.start()

        # connect to peers
        for peer in peers:
            self.connect_peer(peer)

        while True:
            message = sys.stdin.readline().strip()
            if message == "ping":
                for address in self.peers:
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                    self.send_message(self.peers[address],"ping",{"time":current_time})
                    print("pinged:",address)

    def accept_peers(self):
        while True:
            peer_socket, peer_address = self.sock.accept()
            print(f'peer connected: {peer_address}')
            self.receive_messages_peer(peer_socket)
            self.send_message(peer_socket,"address",{"address":self.address})

    def connect_peer(self,peer):
        try:
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sock.connect(peer)
            print("connected to peer:",peer)
            self.receive_messages_peer(sock)
            self.send_message(sock,"address",{"address":self.address})
        except:
            print("connection failed:",peer)

    def receive_messages_peer(self,sock):
        def receive():
            while True:
                message = sock.recv(4096)
                if not message:
                    sock.close()
                    break
                self.handle_message(sock,pickle.loads(message))

        receive_thread = threading.Thread(target=receive,args=())
        receive_thread.start()

    def handle_message(self,sock,message):
        if message["command"] == "address":
            self.peers[message["data"]["address"]] = sock
            print("added peer", message["data"]["address"])
        elif message["command"] == "ping":
            print("received:",message)
            self.send_message(sock,"pong",{"time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")})
            print("ponged:",self.get_address(sock))
        elif message["command"] == "pong":
            print("received:", message)

    def send_message(self,sock,command,data):
        sock.send(pickle.dumps({"command":command,"data":data}))

    def get_address(self,socket):
        return list(self.peers.keys())[list(self.peers.values()).index(socket)]


# Create a peer
peer = Peer("localhost", 8000)
