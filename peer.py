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
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

class Peer:
    def __init__(self, tracker_address, tracker_port,initial_number,logger):
        self.logger = logger
        # Initialize Peer
        self.peers_sockets = {}
        self.peers_publickeys = {}
        self.socknames = set()
        self.circuits = {}

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('localhost', 0))
        self.sock.listen()
        
        self.address = uuid.uuid4().hex
        self.log("socket initialized " , self.address)

        self.privatekey = rsa.generate_private_key(public_exponent=65537, key_size=1024)
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
            if self.sock.getsockname()[1] != peer[1]:
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
        circuit_id = cell.get_circuit_id()
        match command:
            case "circuit":
                self.initialize_circuit(circuit_id,data)
            case "peers":
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
                message = self.privatekey.decrypt(data["message"],padding=padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                ).decode()
                if circuit_id not in self.get_circuits():
                    self.log(" - - - - end - - - -")
                    self.log(message)
                else:
                    self.send_message(circuit_id,{"message":message}, self.get_peer_socket(self.get_circuit_address(circuit_id)))

    def initialize_circuit(self,circuit_id,data):
        self.log(data)
        next_peer_address = data["next"][0]
        self.circuits[circuit_id] = next_peer_address
        remaining_peers_addresses = data["next"][1:]
        if len(remaining_peers_addresses) > 0:
            cell = Cell(circuit_id,"circuit",{"next":remaining_peers_addresses})
            self.send_cell(cell,self.get_peer_socket(next_peer_address))
        self.log(self.circuits)

    def send_message(self,circuit_id,message,sock):
         current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
         address = self.get_address_from_socket(sock)
         cell = Cell(circuit_id,"message",{"time":current_time,"message":message})
         self.send_cell(cell,sock)
         self.log("sent message to ",address, " : ",  message)

    def encrypt_with_publickey(self,message,publickey):
        return publickey.encrypt(message,
             padding.OAEP(
                 mgf=padding.MGF1(algorithm=hashes.SHA256()),
                 algorithm=hashes.SHA256(),
                 label=None
         ))

    def aes_encrypt(self,message,cipher):
        encrypted_message = cipher.encrypt(message)
        return encrypted_message

    def aes_decrypt(self,message,decipher):
        decrypted_message = decipher.decrypt(message)
        return decrypted_message

    def create_message_cell(self,circuit_id,message,addresses):
       key = get_random_bytes(16)
       cipher = AES.new(key, AES.MODE_EAX)
       nonce = cipher.nonce
       encrypted_message = self.aes_encrypt(message,cipher)

       for address in addresses:
           publickey = self.get_peer_publickey(address)
           key = self.encrypt_with_publickey(key,publickey)
           nonce = self.encrypt_with_publickey(nonce,publickey)
       return Cell(circuit_id,"message",{"message":encrypted_message,"nonce":nonce,"key":key})

    def pong(self,sock):
        cell = Cell("NA","pong",{"time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")})
        self.send_cell(cell,sock)
        self.log("ponged : " , self.get_address_from_socket(sock))

    def ping(self,sock):
        cell = Cell("NA","ping",{"time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")})
        self.send_cell(cell,sock)
        self.log("pinged : " , self.get_address_from_socket(sock))

    def send_sockname(self):
        # send peer socket to tracker
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

    def get_peer_publickey(self,address):
        return self.peers_publickeys[address]

    def get_circuits(self):
        return self.circuits

    def get_circuit_address(self,circuit):
        return self.circuits[circuit]

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
