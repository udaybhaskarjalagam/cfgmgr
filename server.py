import socket
import json
import argparse
import threading
import logging
import os

class Server:

    def __init__(self):
        pass

    def performactionforclient(self, clientaddr, actions):
        """
        :param clientaddr:  client to perform action on
        :param actions: dictionary of actions to perform on each clients
        :return: Logs details about the actions submitted to client, it including any success or error messages as well. For simplicity of the tool will be printing only status of the actions not the complete output.
        """
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
            client.connect((clientaddr, 9999))                               # connect the client    client.connect((target, port))
            client.send(str(actions).encode())                           # Have to send data in binary format
            response = client.recv(4096)                                 # Most cases recomended buffer size , could increase or decrease based on requirements
            print("{0}: {1}".format(client, response.decode()))
        except:
            logging.exception("ErrorL while connecting to remote server {0}".format(client))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="config manger tool to perform operations on remote servers")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--clients", nargs='+', help="List of Clients seperated by , to perform actions")
    group.add_argument("-g", "--groups",  nargs='+', help="List of Groups seperated by , to perform actions")
    parser.add_argument("-a", "--actions", help="Configuration files to perform actions on the clients, this is json file", default='./cfg/runactions.json')
    args = parser.parse_args()

    if len(vars(args)) == 0:
        logging.info("Please enter appropriate input to perform operations.")
        parser.print_help()

    #
    #     Check if clients are provided and exist program if not given appropriate details.
    #
    listofclients = []

    if not len(args.clients) == 0:
        listofclients = args.clients
    elif not len(args.groups) == 0:
        with open('./cfg/clientcfg.json') as clientgrousp:
            groupsdata = json.load(clientgrousp)
            for grp in args.groups:
                try:
                    listofclients = listofclients +groupsdata["groups"][grp]
                except KeyError:
                    logging.error("{0} group doesn't exist in client configuration files".format(grp))

    if len(listofclients) == 0:
        logging.error("There are no clients to perform operations, please enter clients list or groups list")
        parser.print_help()
        exit(100)
    #
    # Check if the configuration file exists
    #
    argmentdict = {}
    if not os.path.isfile(args.actions):
        logging.error("Action configuration file doesn't exist.")
        parser.print_help()
        exit(101)
    else:
        with open(args.actions) as actionsfile:
            argmentdict = json.load(actionsfile)

    srv = Server()
    for client in listofclients:
        client_handler = threading.Thread(
            target=srv.performactionforclient,
            args=(client, argmentdict)
        )
        client_handler.start()









# # create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
# # connect the client
# # client.connect((target, port))
# client.connect(('192.168.1.101', 9999))
#
# #load the client configuration file
# with open('./cfg/clientcfg.json') as clicfg:
#     clientcfgdata = json.load(clicfg)
#
# # send some data (in this case a HTTP GET request)
# client.send(str(clientcfgdata).encode())
#
# # receive the response data (4096 is recommended buffer size)
# response = client.recv(4096)
#
# print(response.decode())
#
#


