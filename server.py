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
        self.packet_received = ()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0' , self.port))
        self.ip_address = self.sock.getsockname()[0]
        #self.received_sender_ids = set()
        #self.ip_addresses = self.get_ip_addresses()

        print(f'Router initialised!')
        #print('IP ADDRESS',self.ip_address)


    # def get_ip_addresses(self):
    #     addresses = {}
        
    #     # Get address information for all available network interfaces
    #     for res in socket.getaddrinfo(socket.gethostname(), None):
    #         af, socktype, proto, canonname, sockaddr = res

    #         # Filter out IPv4 and IPv6 addresses
    #         if af == socket.AF_INET or af == socket.AF_INET6:
    #             interface_name = sockaddr[0]
    #             ip_address = sockaddr[0]

    #             # Store the IP address in the dictionary
    #             if interface_name not in addresses:
    #                 addresses[interface_name] = []
    #             addresses[interface_name].append(ip_address)
    #     addresses = list(addresses.keys())
    #     print('ADDRESSES', addresses, type(addresses))
    #     return addresses


    
    def broadcast(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        msg_to_relay, received_msg_ip_address = self.packet_received
        
        header_size = struct.calcsize('i')
        sender_id = (struct.unpack('i',  msg_to_relay[:header_size]))[0]
        
        received_msg_ip_address = ipaddress.ip_address(received_msg_ip_address[0])
        print(received_msg_ip_address)

        # if sender_id in self.received_sender_ids:
        #     print('DEBUG: Sender ID =', sender_id)
        #     return
        #print(f'Received {msg_to_relay.decode()}')
        for network in self.connected_networks:
            network = network + '0/24'
            for ip in ipaddress.IPv4Network(network):
                self.sock.sendto(msg_to_relay, (str(ip), self.port))



    def listen(self):
        while True:
            received_packet = self.sock.recvfrom(self.buffersize)
            self.packet_received = received_packet

            header_size = struct.calcsize('i')
            sender_id = (struct.unpack('i',  received_packet[0][:header_size]))[0]

            contents_of_msg = received_packet[0][header_size:].decode()

            self.broadcast()

            #self.received_sender_ids.add(sender_id)
            #print('DEBUG: set =',self.received_sender_ids)
    

def main(argv):
    e = Router(argv)
    print(f'Connected networks to the router: {e.connected_networks}')
    e.listen()

if __name__ == '__main__':
    main(sys.argv[1:])