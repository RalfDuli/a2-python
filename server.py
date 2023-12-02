import socket
import sys
import struct
import time
import threading

class Router:

    # argv follows the format: [list_of_connected_networks, time_to_wait_before_initialising]
    def __init__(self, argv) -> None:
        self.buffersize = 50000
        self.port = 5000
        self.connected_networks = argv[:-1]
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0' , self.port))
        self.ip_address = self.sock.getsockname()[0]
        self.received_sender_ids = set()
        self.received_ips = {}
        self.forwarding_table = {}
        self.endpoint_dict = {}

        # Wait until sending data.
        time.sleep(float(argv[-1]))

        print(f'Router initialised!')

    def broadcast(self, msg_to_relay):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        header_size = struct.calcsize('iii')
        sender_id = (struct.unpack('iii',  msg_to_relay[:header_size]))[0]
        
        if sender_id in self.received_sender_ids:
            return
        for network in self.connected_networks:
            network = network + '255'
            
            self.sock.sendto(msg_to_relay, (network, self.port))

        self.received_sender_ids.add(sender_id)

    def forward_data(self, msg, sender_id):
        adrs_to_relay_to = self.forwarding_table[sender_id]['Next hop']
        self.sock.sendto(msg, adrs_to_relay_to)

    def listen(self):
        while True:
            try:
                received_packet, received_address = self.sock.recvfrom(self.buffersize)
                header_size = struct.calcsize('iii')
                header = struct.unpack('iii',  received_packet[:header_size])
                sender_id = header[0]
                endpoint_to_send_to = header[1]
                msg_type = header[2]

                # Each message has a "msg_type" field in their header.
                # 0 means it is a broadcast.
                # 1 means it is a reply.
                # 2 means it is directly sending data.

                if msg_type == 0:
                    if sender_id not in self.received_ips.keys():
                        self.received_ips[sender_id] = received_address
                    print('Received broadcast from',sender_id)
                    print('Broadcasting message.')
                    

                    if sender_id not in self.endpoint_dict.keys():
                        self.endpoint_dict[sender_id] = endpoint_to_send_to
                    self.broadcast(received_packet)
                    
                elif msg_type == 1:
                    print('Reply from endpoint received.')
                    self.construct_forwarding_table()
                    adrs_to_send_to = self.forwarding_table[sender_id]['Next hop']
                    self.sock.sendto(received_packet, adrs_to_send_to)
                elif msg_type == 2:
                    print('Directly relaying message.')
                    adrs_to_send_to = self.forwarding_table[sender_id]['Next hop']
                    self.forward_data(received_packet, sender_id)
            except KeyError:
                print('Endpoint to send to does not exist.')
                for key in self.forwarding_table.keys():
                    self.forward_data(received_packet, key)

    
    def construct_forwarding_table(self):
        for key in self.received_ips.keys():
            self.forwarding_table[key] = {
                'Origin' : key,
                'Next hop' : self.received_ips[self.endpoint_dict[key]]
            }

def main(argv):
    e = Router(argv)
    print(f'Connected networks to the router: {e.connected_networks}')
    listening_thread_1 = threading.Thread(target=e.listen())
    listening_thread_2 = threading.Thread(target=e.listen())
    listening_thread_1.start()
    listening_thread_2.start()
    listening_thread_1.join()
    listening_thread_2.join()

if __name__ == '__main__':
    main(sys.argv[1:])