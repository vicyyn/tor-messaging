### Tor based messaging system

- [x] basic peer to peer communication

- [x] private/public key messaging between 2 peers

- [x] send and handle commands

- [x] private/public key messages encryption

- [x] limit number of peers, randomize node picking

- [x] client graphical user interface (GUI)

- [x] diffie hellman key exchange

- [x] create circuit

- [x] onion encryption

- [ ] client messaging in the network

### Communication between nodes

- When a node tries to connect to the network, it will start by connecting to the tracker which consequentially returns the the addresses of the nodes in order to establish a peer to peer connection.

- Any data send between a node and the tracker or from node to node will obey this structure: [command] [data]

  - command: ping, send, set address...

  - data: data that needs to be handled when receiving the command.
