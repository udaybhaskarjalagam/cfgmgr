from lib.common import Common, Requestprocessing
import socket
import threading
import ast
import logging
logger = logging.getLogger('myapp')
hdlr = logging.FileHandler('./log/client.log')
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.WARNING)


class Client:

    def __init__(self):
        self.bind_ip = '0.0.0.0'
        self.bind_port = 9966
        self.cfgmgrclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cfgmgrclient.bind((self.bind_ip, self.bind_port))
        self.cfgmgrclient.listen(10)  # max backlog of connections
        logger.info('Listening on {}:{}'.format(self.bind_ip, self.bind_port))


    def startclient(self):
        while True:
            server_sock, address = self.cfgmgrclient.accept()
            logger.info('Accepted connection from {}:{}'.format(address[0], address[1]))
            client_handler = threading.Thread(
                target=self.__client_connection_operations,
                args=(server_sock,)
            )
            client_handler.start()


    def __client_connection_operations(self, server_socket):
        try:
            request = server_socket.recv(4096)
            req_data = ast.literal_eval(request.decode())
            reqproces = Requestprocessing()
            try:
                reqproces.requestprocess(server_socket, req_data)
            except:
                logger.exception("Error while doing operations")
                server_socket.send('Error while doing operations'.encode())
            server_socket.send('Request process completed'.encode())
            server_socket.send('PROGRAMCOMPLETED'.encode())
            server_socket.close()
        except:
            server_socket.close()
            logger.exception("Error while doing operations")



if __name__ == '__main__':
    client = Client()
    client.startclient()
