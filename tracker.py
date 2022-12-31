#/usr/bin/python3

import socket
import random
import threading
from cell import CELL_SIZE, Cell

class Tracker:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('localhost', 8000))
        self.sock.listen()
        self.peers = []
        print("tracker initialized")

        print("listening for peers")
        while True:
            connection , address = self.sock.accept()
            print("new peer connected",address);
            threading.Thread(target=self.listen_for_cells,args=(connection,)).start()

    def listen_for_cells(self,sock):
        while True:
            cell_serialized = sock.recv(CELL_SIZE)
            cell = Cell.deserialize(cell_serialized)
            if cell != None:
                self.handle_cell(cell,sock)
            else:
                break

    def handle_cell(self,cell:Cell,sock):
        cell.log()
        match cell.get_command():
            case "get_peers":
                self.send_peers(cell.get_data(),sock)
            case "sockname":
                self.add_peer(cell.get_data())

    def send_cell(self,cell:Cell,sock):
        sock.sendall(cell.serialize())

    def send_peers(self,number,sock):
        peers = self.get_random_peers(number)
        cell = Cell("NA","peers",peers)
        self.send_cell(cell,sock)
        print("sent peers : ", peers)

    def add_peer(self,peer):
        self.peers.append(peer)
        print("added peer:",peer)

    def get_random_peers(self,number):
        if number > len(self.peers):
            return self.peers
        return random.sample(self.peers,k=number)
        
if __name__ == "__main__":
    Tracker()
