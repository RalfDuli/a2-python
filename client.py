import socket
import os
import subprocess
import json
import docker
import sys

class Endpoint:
    def __init__(self) -> None:
        self.port = 5000
        self.container_id = self.get_container_id()


    """ def get_container_ip(self, container_id):
        try:
            command = f"docker inspect --format='{{.NetworkSettings.IPAddress}}' {container_id}"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            ip_address = result.stdout.strip()  # Remove newline characters
            return ip_address

        except subprocess.CalledProcessError as e:
            print(f"Error executing Docker command: {e}")
            return None



    def get_networks(self, container_id):
        try:
            client = docker.DockerClient(base_url='unix://var/run/docker.sock')  # Manually specifying the Unix socket
            container = client.containers.get(container_id)
            networks = container.attrs['NetworkSettings']['Networks']
            return networks.keys()
        except docker.errors.NotFound as e:
            print(f"Container not found: {e}")
            return None
        except docker.errors.APIError as e:
            print(f"API error: {e}")
            return None """

    def get_container_id(self):
        container_id = os.getenv("HOSTNAME")
        return container_id
    

def main(argv):
    e = Endpoint()
    print('hi')

    while True:
        pass

if __name__ == '__main__':
    main(sys.argv[1:])