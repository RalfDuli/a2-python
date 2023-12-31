import socket
import sys
import random
import struct
import time

class Endpoint:

    # argv follows the format [connected_network, endpoint_ID, endpoint_to_send_to_ID]
    def __init__(self, argv) -> None:
        self.buffersize = 50000
        self.port = 5000
        self.connected_network = argv[0]
        self.id = int(argv[2])
        self.endpoint_to_send_to = int(argv[1])
        self.msg = f"Message from endpoint {self.id}"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(('0.0.0.0', self.port))
        self.endpoint_ip = socket.gethostbyname(socket.gethostname())
        self.received_sender_ids = set()
        self.adjacent_router_adrs = None

        print(f'Endpoint {self.id} initialised!')
    
    def generate_random_number(self):
        return random.randint(0,10000) + random.randint(0,10000) + random.randint(0,10000)
    
    def broadcast(self):
        network = self.connected_network

        print('connected network:',self.connected_network)
        print('Sending message to network.')

        network_to_send_to = network + '255'
        print(f'network to send to: {network_to_send_to}')
        data = f'Broadcast from endpoint {self.id}'
        msg_to_send = struct.pack('HHH', self.id, self.endpoint_to_send_to, 0) + data.encode()
        self.sock.sendto(msg_to_send, (network_to_send_to, self.port))

    def listen(self):
        while True:
            received_packet, received_address = self.sock.recvfrom(self.buffersize)
            self.adjacent_router_adrs = received_address

            header_size = struct.calcsize('HHH')
            header = struct.unpack('HHH',  received_packet[:header_size])
            sender_id = header[0]
            endpoint_to_send_to = header[1]
            msg_type = header[2]
            contents_of_msg = received_packet[header_size:].decode()

            # Each message has a "msg_type" field in their header.
            # 0 means it is a broadcast.
            # 1 means it is a reply.
            # 2 means it is directly sending data.
            # 3 means it is signing out of the network.

            if msg_type == 0:
                if sender_id != self.id and sender_id not in self.received_sender_ids:
                    print(contents_of_msg)
                    self.received_sender_ids.add(sender_id)
                    self.reply_to_broadcast()

            elif msg_type == 1 and endpoint_to_send_to == self.id:
                self.send_msg()
            
            elif msg_type == 2:
                print(contents_of_msg)
                time.sleep(20) # Waits 10 seconds to sign out.
                self.sign_out()

    def send_msg(self):
        # The header design is as such:
        # [endpoint_ID, endpoint_to_send_to, type_of_message]
        header = struct.pack('HHH', self.id, self.endpoint_to_send_to, 2)
        msg_to_send = header + self.msg.encode()
       
        self.sock.sendto(msg_to_send, self.adjacent_router_adrs)

    def reply_to_broadcast(self):
        reply = 'Reply to broadcast.'.encode()
        reply = struct.pack('HHH', self.id, self.endpoint_to_send_to, 1) + reply
        self.sock.sendto(reply, self.adjacent_router_adrs)
        print('Reply made!')

    def sign_out(self):
        signout_msg = 'Signing out'.encode()
        signout_msg = struct.pack('HHH', self.id, self.endpoint_to_send_to, 3) + signout_msg
        self.sock.sendto(signout_msg, self.adjacent_router_adrs)
        print('Signing out!')


def main(argv):
    e = Endpoint(argv)
    time.sleep(random.uniform(0,5))
    e.broadcast()
    e.listen()

if __name__ == '__main__':
    main(sys.argv[1:])  