#/usr/bin/python3

import socket
import threading
import time
import uuid
import datetime
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cell import CELL_SIZE, Cell

class Peer:
    def __init__(self, tracker_address, tracker_port,initial_number,logger):
        self.logger = logger
        # Initialize Peer
        self.peers_sockets = {}
        self.peers_publickeys = {}
        self.socknames = set()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('localhost', 0))
        self.sock.listen()
        
        self.address = uuid.uuid4().hex
        self.log("socket initialized " , self.address)
        self.privatekey = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.publickey = self.privatekey.public_key()

        # Connect to Tracker
        self.tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tracker.connect((tracker_address, tracker_port))
        self.log("connected to tracker")
        threading.Thread(target=self.listen_for_cells,args=(self.tracker,)).start()

        self.get_peers(initial_number)
        self.send_sockname()

        # listen for connections
        accept_thread = threading.Thread(target=self.accept_peers,args=())
        accept_thread.start()

        # connect to peers
        for peer in self.socknames:
            self.connect_peer(peer)

    def accept_peers(self):
        while True:
            peer_socket, peer_address = self.sock.accept()
            threading.Thread(target=self.listen_for_cells,args=(peer_socket,)).start()
            self.initialize_peer(peer_socket)
            self.log(f'peer connected : {peer_address}')

    def connect_peer(self,peer):
        try:
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sock.connect(peer)
            threading.Thread(target=self.listen_for_cells,args=(sock,)).start()
            self.initialize_peer(sock)
            self.log("connected to peer : " , peer)
        except:
            self.log("connection failed : " , peer)

    def initialize_peer(self,sock):
        cell = Cell("NA","init",{"address":self.address,"publickey":self.publickey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )})
        self.send_cell(cell,sock)

    def listen_for_cells(self,sock):
        while True:
            cell_serialized = sock.recv(CELL_SIZE)
            cell = Cell.deserialize(cell_serialized)
            if cell != None:
                self.handle_cell(cell,sock)
            else:
                break

    def handle_cell(self,cell,sock):
        command = cell.get_command()
        data = cell.get_data()
        match command:
            case "peers":
                self.log("received peers : " , data)
                for peer in data:
                    if peer not in self.socknames:
                        self.socknames.add(peer)
                        self.connect_peer(peer)
            case "init":
                self.peers_sockets[data["address"]] = sock
                self.peers_publickeys[data["address"]] = serialization.load_pem_public_key(data["publickey"],backend=default_backend())
                self.log("added peer : " , data["address"])
            case "ping":
                self.log("received ping : " , cell.get_data())
                self.pong(sock)
            case "pong":
                self.log("received pong : " , cell.get_data())
            case "message":
                self.log(" - - - - received message - - - -")
                self.log(self.privatekey.decrypt(data["message"],padding=padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                ).decode())
            case other:
                pass

    def pong(self,sock):
        cell = Cell("NA","pong",{"time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")})
        self.send_cell(cell,sock)
        self.log("ponged : " , self.get_address_from_socket(sock))

    def ping(self,sock):
        cell = Cell("NA","ping",{"time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")})
        self.send_cell(cell,sock)
        self.log("pinged : " , self.get_address_from_socket(sock))

    def send_sockname(self):
        # Send Peer Socket to Tracker
        cell = Cell("NA","sockname",self.sock.getsockname())
        self.send_cell(cell,self.tracker)

    def get_peers(self,number):
        cell = Cell("NA","get_peers",number)
        self.send_cell(cell,self.tracker)
        # needed when creating multiple peers sequentially
        time.sleep(0.5)

    def send_cell(self,cell:Cell,sock):
        sock.sendall(cell.serialize())

    def get_address_from_socket(self,socket):
        return list(self.peers_sockets.keys())[list(self.peers_sockets.values()).index(socket)]

    def get_peers_addresses(self):
        return self.peers_publickeys.keys()

    def get_address(self):
        return self.address

    def get_peers_sockets(self):
        return self.peers_sockets

    def get_peers_publickeys(self):
        return self.peers_publickeys

    def get_socket(self):
        return self.sock

    def get_peer_socket(self,address):
        return self.peers_sockets[address]

    def log(self,*messages):
        message = ""
        for m in messages:
            message = message + str(m)
        if self.logger:
            self.logger.log(message)
        else:
            print(message)


if __name__ == "__main__":
    number = int(input("how many peers do you want to start (the bigger the more decetralized the network will be):\n"))
    for i in range(number):
        Peer("localhost",8000,3,None)
        time.sleep(0.5)
