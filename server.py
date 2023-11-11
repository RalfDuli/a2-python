import socket
import os
import sys
import random
import threading
import time
import struct

class Router:

    def __init__(self, connected_networks) -> None:
        self.buffersize = 50000
        self.port = 5000
        self.connected_networks = connected_networks
        self.id = random.randint(0,10000)
        self.packet_received = ()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0' , self.port))

        print(f'Router initialised!')


    
    def broadcast(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        msg_to_relay, received_msg_ip_address = self.packet_received

        received_msg_ip_address = received_msg_ip_address[0]
        received_msg_ip_address = received_msg_ip_address.split('.')
        received_msg_ip_address = '.'.join(received_msg_ip_address[:3])
        received_msg_ip_address = received_msg_ip_address + '.'

        """ string = "A.B.C.D"
        parts = string.split('.')  # Split the string by the '.' delimiter
        result = '.'.join(parts[:3])  # Join the first three elements using '.' as a separator

        print(result) """

        if self.packet_received != ():
            for network in self.connected_networks:
                if network != received_msg_ip_address:
                    print(
                    f'NETWORK!!! {network} | COMPARING TO: {received_msg_ip_address}'
                    )
                    network_to_send_to = network + '255'
                    print(f'Relaying msg to network: {network_to_send_to}')
                    self.sock.sendto(msg_to_relay, (network_to_send_to, self.port))

            self.packet_received = ()

    def receive(self):
        while True:
            received_packet = self.sock.recvfrom(self.buffersize)
            self.packet_received = received_packet

            header_size = struct.calcsize('i')
            contents_of_msg = received_packet[0][header_size:].decode()
            print(f'Received {contents_of_msg}')

            self.broadcast()
    

def main(argv):
    e = Router(argv)
    print(f'Connected networks to the router: {e.connected_networks}')
    e.receive()

if __name__ == '__main__':
    main(sys.argv[1:])