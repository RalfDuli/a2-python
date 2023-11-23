import socket
import sys
import random
import struct
import time

class Endpoint:

    def __init__(self, connected_network) -> None:
        self.buffersize = 50000
        self.port = 5000
        self.connected_network = connected_network[0]
        self.id = self.generate_random_number()
        self.msg = f"Message from endpoint {self.id}"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(('0.0.0.0', self.port))
        self.endpoint_ip = socket.gethostbyname(socket.gethostname())
        self.received_sender_ids = set()

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
        msg_to_send = struct.pack('ii', self.id, 0) + data.encode()
        self.sock.sendto(msg_to_send, (network_to_send_to, self.port))

    def receive_broadcast(self):
        received_packet, _ = self.sock.recvfrom(self.buffersize)
        header_size = struct.calcsize('ii')
        sender_id = (struct.unpack('ii',  received_packet[:header_size]))[0]
        msg_type = (struct.unpack('ii',  received_packet[:header_size]))[1]
        if sender_id != self.id and sender_id not in self.received_sender_ids:
            contents_of_msg = received_packet[header_size:].decode()
            print(contents_of_msg)
            self.received_sender_ids.add(sender_id)
        while True:
            pass

    def reply_to_broadcast(self):
        pass


def main(argv):
    e = Endpoint(argv)
    print(e.connected_network)
    time.sleep(random.uniform(0,5))
    e.broadcast()
    e.receive_broadcast()

if __name__ == '__main__':
    main(sys.argv[1:])  