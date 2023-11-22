import socket
import sys
import struct
import ipaddress
import time

class Router:

    def __init__(self, connected_networks) -> None:
        self.buffersize = 50000
        self.port = 5000
        self.connected_networks = connected_networks[:-1]
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0' , self.port))
        self.ip_address = self.sock.getsockname()[0]
        self.received_sender_ids = set()

        # Wait until sending data. Simply a stylistic choice.
        time.sleep(float(connected_networks[-1]))

        print(f'Router initialised!')

    def broadcast(self, msg_to_relay):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        header_size = struct.calcsize('i')
        sender_id = (struct.unpack('i',  msg_to_relay[:header_size]))[0]
        
        if sender_id in self.received_sender_ids:
            return
        for network in self.connected_networks:
            network = network + '0/24'
            for ip in ipaddress.IPv4Network(network):
                self.sock.sendto(msg_to_relay, (str(ip), self.port))
        self.received_sender_ids.add(sender_id)

    def listen(self):
        while True:
            received_packet, _ = self.sock.recvfrom(self.buffersize)

            self.broadcast(received_packet)

def main(argv):
    e = Router(argv)
    print(f'Connected networks to the router: {e.connected_networks}')
    e.listen()

if __name__ == '__main__':
    main(sys.argv[1:])