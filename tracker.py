import socket
import pickle

class Tracker:
    def __init__(self):
        # Create a socket object
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Get the local hostname
        self.host = socket.gethostname()

        # Set the port number
        self.port = 12345

        # Bind the socket to the host and port
        self.sock.bind((self.host, self.port))

        # Listen for incoming connections
        self.sock.listen()

        # Create a list to store the connections
        self.peers = []

    def run(self):
        while True:
            # Accept an incoming connection
            connection , address = self.sock.accept()

            # Store the connection's address and port
            self.peers.append(address)
            data = pickle.dumps(self.peers)
            connection.sendall(data)
            print("new peer added",connection);
        
# Create a tracker
tracker = Tracker()

# Accept incoming connections indefinitely
tracker.run()
