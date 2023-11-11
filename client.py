import socket
import os
import sys
import random
import threading
import time
import struct

class Endpoint:

    def __init__(self, connected_network) -> None:
        self.buffersize = 50000
        self.port = 5000
        self.connected_network = connected_network[0]
        self.id = random.randint(0,10000)
        self.msg = f"Message from endpoint {self.id}"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0' , self.port))

        print(f'Endpoint {self.id} initialised!')
    
    def broadcast(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        network = self.connected_network
        network_to_send_to = network + '255'
        print(f'network to send to: {network_to_send_to}')
        msg_to_send = struct.pack('i', self.id) + self.msg.encode()
        self.sock.sendto(msg_to_send, (network_to_send_to, self.port))

    def receive(self):
        while True:
            received_packet, _ = self.sock.recvfrom(self.buffersize)
            header_size = struct.calcsize('i')
            sender_id = (struct.unpack('i',  received_packet[:header_size]))[0]
            if sender_id != self.id:
                contents_of_msg = received_packet[header_size:].decode()
                print(contents_of_msg)
    

def main(argv):
    e = Endpoint(argv)
    print(e.connected_network)
    
    sending_thread = threading.Thread(target=e.broadcast)
    receiving_thread = threading.Thread(target=e.receive)

    receiving_thread.start()
    time.sleep(0.02)
    sending_thread.start()

    sending_thread.join()
    receiving_thread.join()

if __name__ == '__main__':
    main(sys.argv[1:])