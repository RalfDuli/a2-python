import socket
import sys
import random
import struct
import ipaddress

class Router:

    def __init__(self, connected_networks) -> None:
        self.buffersize = 50000
        self.port = 5000
        self.connected_networks = connected_networks
        #self.router_ip = socket.gethostbyname(socket.gethostname())
        self.id = random.randint(0,10000)
        self.packet_received = ()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0' , self.port))
        self.ip_address = self.sock.getsockname()[0]

        print(f'Router initialised!')
        print('IP ADDRESS',self.ip_address)


    
    def broadcast(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        msg_to_relay, received_msg_ip_address = self.packet_received

        received_msg_ip_address = ipaddress.ip_address(received_msg_ip_address[0])
        print(received_msg_ip_address)

        #for network in self.connected_networks:
        #    network_to_broadcast_to = network + '255'
        #    self.sock.sendto(msg_to_relay, (network_to_broadcast_to, self.port))
        
        for network in self.connected_networks:
            network = network + '0/24'

            for ip in ipaddress.IPv4Network(network):
                if ip != received_msg_ip_address and ip != self.ip_address:
                    
                    self.sock.sendto(msg_to_relay, (str(ip), self.port))
                    #print(f"Message sent to {broadcast_address}")
                else:
                    print('very nice! IP =', ip)


    def listen(self):
        while True:
            received_packet = self.sock.recvfrom(self.buffersize)
            print(received_packet)
            self.packet_received = received_packet

            if received_packet[1][0] == self.ip_address:
                continue

            header_size = struct.calcsize('i')
            contents_of_msg = received_packet[0][header_size:].decode()
            print(f'Received {contents_of_msg}')

            self.broadcast()
    

def main(argv):
    e = Router(argv)
    print(f'Connected networks to the router: {e.connected_networks}')
    e.listen()

if __name__ == '__main__':
    main(sys.argv[1:])