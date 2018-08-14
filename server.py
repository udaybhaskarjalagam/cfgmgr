from lib.common import Requestprocessing
import socket
import json
import argparse
import threading
import multiprocessing
import logging
import os

logger = logging.getLogger('myapp')
hdlr = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

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
            client.connect((clientaddr, 9966))                           # connect the client    client.connect((target, port))
            client.send(str(actions).encode())                           # Have to send data in binary format
            while True:
                response = client.recv(4096)                                        # Most cases recomended buffer size , could increase or decrease based on requirements
                if response:
                    if "PROGRAMCOMPLETED" in response.decode():
                        logger.info("{0}: {1}".format(clientaddr, response.decode().replace("PROGRAMCOMPLETED", "") ))
                        break
                    logger.info("{0}: {1}".format(clientaddr, response.decode()))


        except:
            logger.exception("Error while connecting to remote server {0}".format(clientaddr))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="config manger tool to perform operations on remote servers")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--clients", nargs='+', help="List of Clients seperated by space to perform actions")
    group.add_argument("-g", "--groups",  nargs='+', help="List of Groups seperated by space to perform actions")
    parser.add_argument("-a", "--actions", help="Configuration files to perform actions on the clients, this is json file", default='./cfg/runactions.json')
    args = parser.parse_args()

    if len(vars(args)) == 0:
        logger.info("Please enter appropriate input to perform operations.")
        parser.print_help()

    #
    #     Check if clients are provided and exist program if not given appropriate details.
    #
    listofclients = []

    if args.clients != None:
        if not len(args.clients) == 0:
            listofclients = args.clients
    if args.groups != None:
        if  not len(args.groups) == 0:
            if not os.path.isfile("./cfg/clientcfg.json"):
                logger.error("Trying to access groups details but ./cfg/clientcfg.json doesn't exist.")
            with open('./cfg/clientcfg.json') as clientgrousp:
                groupsdata = json.load(clientgrousp)
                for grp in args.groups:
                    try:
                        listofclients = listofclients +groupsdata["groups"][grp]
                    except KeyError:
                        logger.error("{0} group doesn't exist in client configuration files".format(grp))

    if len(listofclients) == 0:
        logger.error("There are no clients to perform operations, please enter clients list or groups list")
        parser.print_help()
        exit(100)


    #
    # Check if the configuration file exists
    #
    argmentdict = {}
    if not os.path.isfile(args.actions):
        logger.error("Action configuration file doesn't exist.")
        parser.print_help()
        exit(101)
    else:
        with open(args.actions) as actionsfile:
            argmentdict = json.load(actionsfile)


    #
    # Validating configuration file to check if required data is provided to execute each request.
    # And also reads source file for file operations and append it as data to action dictionary
    #

    reqmethods = Requestprocessing()
    for order in argmentdict.keys():
        if not reqmethods.reqvalidateion(argmentdict[order]):
            logger.error("Validation failed , please correct runactions file and start again.")
        elif list(argmentdict[order].keys())[0] == "file":
            if argmentdict[order]["file"]["action"] in ["write", "create"]:
                if os.path.isfile(argmentdict[order]["file"]["sourcepath"]):
                    with open(argmentdict[order]["file"]["sourcepath"]) as srcfile:
                        argmentdict[order]["file"]["data"] = srcfile.read()

    logger.info("Configuration is valid, will proceed to execute")
    srv = Server()
    jobs = []
    for client in listofclients:
        thread = multiprocessing.Process(
            target=srv.performactionforclient,
            args=(client, argmentdict)
        )
        jobs.append(thread)

    for jb in jobs:
        jb.start()

    for jb in jobs:
        jb.join()
