from lib.common import Common, Requestprocessing
import socket
import threading
import time
import json
import ast
import logging

class Client:

    def __init__(self):
        self.bind_ip = '0.0.0.0'
        self.bind_port = 9966
        self.cfgmgrclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cfgmgrclient.bind((self.bind_ip, self.bind_port))
        self.cfgmgrclient.listen(10)  # max backlog of connections
        logging.info('Listening on {}:{}'.format(self.bind_ip, self.bind_port))


    def startclient(self):
        while True:
            server_sock, address = self.cfgmgrclient.accept()
            print('Accepted connection from {}:{}'.format(address[0], address[1]))
            client_handler = threading.Thread(
                target=self.__client_connection_operations,
                args=(server_sock,)
            )
            client_handler.start()


    def __client_connection_operations(self, server_socket):
        request = server_socket.recv(4096)
        req_data = ast.literal_eval(request.decode())
        reqproces = Requestprocessing()
        reqproces.requestprocess(server_socket, req_data)
        server_socket.send('Request process completed'.encode())
        server_socket.close()


if __name__ == '__main__':
    client = Client()
    client.startclient()



