import socket
import threading
import pickle
import random

class Peer:
    def __init__(self, tracker_address, tracker_port):
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the tracker
        sock.connect((tracker_address, tracker_port))
        print("connected to tracker")

        # Get the peers
        peers = sock.recv(4096)

        self.peers = pickle.loads(peers)
        print(f'Received peers: {self.peers}')
        sock.close()

        # Create a socket object
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Get the local hostname
        self.host = socket.gethostname()

        # Set the port number
        self.port = random.randint(1024, 65535)

        # Bind the socket to the host and port
        self.sock.bind((self.host, self.port))

        # Listen for incoming connections
        self.sock.listen()

    def send_message(self):
        pass

    def receive_message(self):
        while True:
            message = self.sock.recv(4096)
            print(f'Received response: {message.decode()}')

    def accept_peer(self):
        while True:
            pass


# Create a peer
peer = Peer("localhost", 12345)

# Create the threads
send_thread = threading.Thread(target=peer.send_message)
receive_thread = threading.Thread(target=peer.receive_message)

# Start the threads
send_thread.start()
receive_thread.start()

# Wait for the threads to finish
send_thread.join()
receive_thread.join()

