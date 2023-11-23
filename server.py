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
        self.received_ips = {}
        self.forwarding_table = {}

        # Wait until sending data.
        time.sleep(float(connected_networks[-1]))

        print(f'Router initialised!')

    def broadcast(self, msg_to_relay):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        header_size = struct.calcsize('ii')
        sender_id = (struct.unpack('ii',  msg_to_relay[:header_size]))[0]
        
        if sender_id in self.received_sender_ids:
            return
        
        for network in self.connected_networks:
            network = network + '0/24'
            for ip in ipaddress.IPv4Network(network):
                self.sock.sendto(msg_to_relay, (str(ip), self.port))

        self.received_sender_ids.add(sender_id)

    def act_on_endpoint_reply(self):
        pass

    def send_data(self):
        pass

    def listen(self):
        while True:
            received_packet, received_address = self.sock.recvfrom(self.buffersize)
            header_size = struct.calcsize('ii')
            sender_id = (struct.unpack('ii',  received_packet[:header_size]))[0]
            msg_type = (struct.unpack('ii',  received_packet[:header_size]))[1]

            self.received_ips[sender_id] = received_address
            #print(f'DEBUG: {self.received_ips}')

            # Each message has a "msg_type" field in their header.
            # 0 means it is a broadcast.
            # 1 means it is a reply.
            # 2 means it is directly sending data.
            if msg_type == 0:
                self.broadcast(received_packet)
            elif msg_type == 1:
                self.construct_forwarding_table()

    def construct_forwarding_table(self):
        for key in self.received_ips.keys():
            self.forwarding_table[key] = {
                'Origin' : key,
                'Next hop' : self.received_ips[key]
            }
        print('DEBUG:', self.forwarding_table)

def main(argv):
    e = Router(argv)
    print(f'Connected networks to the router: {e.connected_networks}')
    e.listen()

if __name__ == '__main__':
    main(sys.argv[1:])