### Tor based messaging system

- [x] basic peer to peer communication

- [ ] private/public key messaging between 2 peers

- [ ] message propagation in the network

- [ ] tor-like message propagation

### Communication between nodes

- When a node tries to connect to the network, it will start by connecting to the tracker which consequentially returns the the addresses of the nodes in order to establish a peer to peer connection.

- Any data send between a node and the tracker or from node to node will obey this structure: [command] [data]

        - command: ping, send, set address...

        - data: data that needs to be handled when receiving the command.
