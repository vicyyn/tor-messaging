#/usr/bin/python3

import socket
import threading
import pickle
import sys
import uuid
import datetime
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend

class Peer:
    def __init__(self, tracker_address, tracker_port):
        # Initialize Peer
        self.peers = {}

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('localhost', 0))
        self.sock.listen()
        
        self.address = uuid.uuid4().hex
        print("socket initialized",self.address)
        self.privatekey = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.publickey = self.privatekey.public_key()

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
            if message == "peers":
                print(self.peers)
            elif message == "ping":
                for address in self.peers:
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                    self.send_request(self.peers[address]["socket"],"ping",{"time":current_time})
                    print("pinged:",address)
            elif "message:" in message:
                for address in self.peers:
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                    self.send_request(self.peers[address]["socket"],"message",{"time":current_time,"message":self.peers[address]["publickey"].encrypt(message.encode(),
                        padding.OAEP(
                            mgf=padding.MGF1(algorithm=hashes.SHA256()),
                            algorithm=hashes.SHA256(),
                            label=None
                        ))
                    })
                    print("messaged:",address)

    def accept_peers(self):
        while True:
            peer_socket, peer_address = self.sock.accept()
            print(f'peer connected: {peer_address}')
            self.receive_messages_peer(peer_socket)
            self.send_request(peer_socket,"init",{"address":self.address,"publickey":self.publickey.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )})

    def connect_peer(self,peer):
        try:
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sock.connect(peer)
            print("connected to peer:",peer)
            self.receive_messages_peer(sock)
            self.send_request(sock,"init",{"address":self.address,"publickey":self.publickey.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )})
        except:
            print("connection failed:",peer)

    def receive_messages_peer(self,sock):
        def receive():
            while True:
                message = sock.recv(4096)
                if not message:
                    sock.close()
                    break
                self.handle_request(sock,pickle.loads(message))

        receive_thread = threading.Thread(target=receive,args=())
        receive_thread.start()

    def handle_request(self,sock,message):
        if message["command"] == "init":
            self.peers[message["data"]["address"]] = {"socket":sock,"publickey":serialization.load_pem_public_key(message["data"]["publickey"],backend=default_backend())}
            print("added peer", message["data"]["address"])
        elif message["command"] == "ping":
            print("received:",message)
            self.send_request(sock,"pong",{"time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")})
            print("ponged:",self.get_address(sock))
        elif message["command"] == "pong":
            print("received:", message)
        elif message["command"] == "message":
            print(" - - - - received message - - - -")
            print("encrypted:",message["data"])
            print("decrypted:",self.privatekey.decrypt(message["data"]["message"],padding=padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            ).decode())

    def send_request(self,sock,command,data):
        sock.send(pickle.dumps({"command":command,"data":data}))

    def get_address(self,socket):
        return list(self.peers.keys())[list(self.peers.values()).index(socket)]


# Create a peer
peer = Peer("localhost", 8000)
