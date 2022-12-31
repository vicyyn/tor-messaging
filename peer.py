#/usr/bin/python3

import socket
import threading
import random
import time
import uuid
import datetime
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cell import CELL_SIZE, Cell

class Peer:
    def __init__(self, tracker_address, tracker_port,number_of_peers):
        # Initialize Peer
        self.peers_sockets = {}
        self.peers_publickeys = {}
        self.peers = []

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
        threading.Thread(target=self.listen_for_cells,args=(self.tracker,)).start()

        # get peers
        cell = Cell("NA","get_peers",number_of_peers)
        self.send_cell(cell,self.tracker)
        time.sleep(0.5)

        # Send Peer Socket to Tracker
        cell = Cell("NA","new_peer",self.sock.getsockname())
        self.send_cell(cell,self.tracker)

        # listen for connections
        accept_thread = threading.Thread(target=self.accept_peers,args=())
        accept_thread.start()

        # connect to peers
        for peer in self.peers:
            self.connect_peer(peer)

    def accept_peers(self):
        while True:
            peer_socket, peer_address = self.sock.accept()
            threading.Thread(target=self.listen_for_cells,args=(peer_socket,)).start()
            self.initialize_peer(peer_socket)
            print(f'peer connected: {peer_address}')

    def connect_peer(self,peer):
        try:
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sock.connect(peer)
            threading.Thread(target=self.listen_for_cells,args=(sock,)).start()
            self.initialize_peer(sock)
            print("connected to peer:",peer)
        except:
            print("connection failed:",peer)

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
                self.peers = data
                print("received peers : ", data)
            case "init":
                self.peers_sockets[data["address"]] = sock
                self.peers_publickeys[data["address"]] = serialization.load_pem_public_key(data["publickey"],backend=default_backend())
                print("added peer", data["address"])
            case "ping":
                print("received:",cell.get_data())
                cell = Cell("NA","pong",{"time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")})
                self.send_cell(cell,sock)
                print("ponged:",self.get_address(sock))
            case "pong":
                print("received:", cell.get_data())
            case "message":
                print(" - - - - received message - - - -")
                print(self.privatekey.decrypt(data["message"],padding=padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                ).decode())
            case other:
                pass

    def send_cell(self,cell:Cell,sock):
        sock.sendall(cell.serialize())

    def get_address(self,socket):
        return list(self.peers_sockets.keys())[list(self.peers_sockets.values()).index(socket)]

    # def handle_input(self,request):
    #         pattern = r"^\(([^,]+),([^)]+)\) : (.*)$"
    #         match = re.search(pattern, request)
    #         if not match:
    #             return
    #         message = match.group(1)
    #         address = match.group(2)
    #         data = match.group(3)

    #         if message == "peers":
    #             print(self.peers_publickeys)
    #             print(self.peers_sockets)
    #         elif message == "ping":
    #             for address in self.peers_sockets:
    #                 current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    #                 self.send_request(self.peers_sockets[address],"ping",{"time":current_time})
    #                 print("pinged:",address)
    #         elif message == "message":
    #             address = address if address in self.peers_sockets else self.get_random_address()
    #             print(address)
    #             current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    #             self.send_request(self.peers_sockets[address],"message",{"time":current_time,"message":self.peers_publickeys[address].encrypt(request.encode(),
    #                 padding.OAEP(
    #                     mgf=padding.MGF1(algorithm=hashes.SHA256()),
    #                     algorithm=hashes.SHA256(),
    #                     label=None
    #                 ))
    #             })
    #             print("messaged:",address)

    def get_random_address(self):
        if not self.peers_sockets:
            return None
        return random.choice(list(self.peers_sockets.keys()))

    def get_peers_addresses(self):
        print(self.peers_publickeys)
        return self.peers_publickeys.keys()

if __name__ == "__main__":
    number = int(input("how many peers do you want to start (the bigger the more decetralized the network will be):\n"))
    for i in range(number):
        Peer("localhost",8000,3)
        time.sleep(0.5)
