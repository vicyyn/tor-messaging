#/usr/bin/python3

# Peers communicate with one another, and with users via a TLS communication with ephemeral keys.
# Using TLS conceals the data on the connection with perfect forward secrecy, and prevents an
# attacker from modifying data on the wire. Traffic passes along these connections in fixed-size cells.

# Each cell is 4096 bytes, and consists of a header and a payload. The header includes a circuit
# identifier (circID) that specifies which circuit the cell refers to (many circuits can be multiplexed
# over the single TLS connection), and a command to describe what to do with the cell’s payload

# commands :
#   new_peer
#   get_peers
#   peers

import pickle

CELL_SIZE = 4096

class Cell:
    def __init__(self,circuit_id,command,data) -> None:
        self.circuit_id = circuit_id
        self.command = command
        self.data = data

    def serialize(self):
        return pickle.dumps({"circuit_id":self.circuit_id,"command":self.command,"data":self.data})

    @staticmethod
    def deserialize(serialized:bytes):
        try:
            deserialized = pickle.loads(serialized)
            return Cell(deserialized["circuit_id"],deserialized["command"],deserialized["data"])
        except:
            return None

    def get_circuit_id(self):
        return self.circuit_id

    def get_command(self):
        return self.command

    def get_data(self):
        return self.data

    def log(self):
        print("circuit id :",self.circuit_id, " | command :",self.command, " | data :",self.data)
