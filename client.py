from lib.common import Common
import socket
import threading
import time
import json
import ast

class Client:

    def __init__(self):
        self.bind_ip = '0.0.0.0'
        self.bind_port = 9966
        self.cfgmgrclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cfgmgrclient.bind((self.bind_ip, self.bind_port))
        self.cfgmgrclient.listen(10)  # max backlog of connections
        print('Listening on {}:{}'.format(self.bind_ip, self.bind_port))


    def startclient(self):
        while True:
            server_sock, address = self.cfgmgrclient.accept()
            print('Accepted connection from {}:{}'.format(address[0], address[1]))
            client_handler = threading.Thread(
                target=self.client_connection_operation,
                args=(server_sock,)
            )
            client_handler.start()


    def client_connection_operation(self, server_socket):
        request = server_socket.recv(4096)
        print(ast.literal_eval(request.decode()))
        server_socket.send('ACK!'.encode())
        server_socket.close()


if __name__ == '__main__':
    client = Client()
    client.startclient()



