import os, subprocess
import logging


class Requestprocessing:
    """
    This class is for general operations of request
    """
    def __init__(self):
        pass

    def reqvalidateion(self, req_details):
        """
        This method validates each request in the details to check if appropriate values are passed in each request. if missing returns the error
        :param req_details: req
        :return: status of the validation.
        """

        # Each order supposed to have only one operation so will reject if more than one
        req_resource = list(req_details.keys())
        if len(req_resource) != 1:
            logging.error('In configuration file you have passed more than one operation : {0}'.format(
                req_details.keys()))
            return False

        if not req_resource[0].lower() in ["pkg", "file", "service"]:
            logging.error('Not a valid resource type in in the request : {0} , please refer document'.format(
                req_resource[0]))
            return False

        if req_resource[0].lower() == "pkg":
            if "name" not in req_details[req_resource[0]].keys() or "action" not in req_details[req_resource[0]].keys():
                logging.error('Resource type {0} missing name or action details in the config file : {1} , please refer document'
                                   .format(req_resource[0], req_details[req_resource[0]].keys()))
                return False

            if req_details[req_resource[0]]["name"] == "" or req_details[req_resource[0]]["name"] == None:
                logging.error('Resource type {0}  name  {1} is not valid in the config file , please refer document'
                                   .format(req_resource[0], req_details[req_resource[0]]["name"]))
                return False
            if req_details[req_resource[0]]["action"] not in ["install", "remove", "installstatus"]:
                logging.error('Resource type {0}  action   {1} is not valid in the config file , please refer document'
                                   .format(req_resource[0], req_details[req_resource[0]]["action"]))
                return False

        if req_resource[0].lower() == "file":

            if "path" not in req_details[req_resource[0]].keys() or "action" not in req_details[req_resource[0]].keys():
                logging.error('Resource type {0} missing path or action details in the config file : {1} , please refer document'
                                   .format(req_resource[0], req_details[req_resource[0]].keys()))
                return False

            if req_details[req_resource[0]]["path"] == "" or req_details[req_resource[0]]["path"] == None:
                logging.error('Resource type {0}  path  {1} is not valid in the config file , please refer document'
                                   .format(req_resource[0], req_details[req_resource[0]]["name"]))
                return False
            if req_details[req_resource[0]]["action"] not in ["chmod", "chown", "create", "remove", "putdata"]:
                logging.error('Resource type {0}  action   {1} is not valid in the config file , please refer document'
                                   .format(req_resource[0], req_details[req_resource[0]]["action"]))
                return False

            if req_details[req_resource[0]]["action"] == "chmod" and "mode" not in req_details[req_resource[0]].keys():
                logging.error('Mode is required for resources {0} when doing chmod operation '.format(req_resource[0]))
                return False

            if req_details[req_resource[0]]["action"] == "chown" and "owner" not in req_details[req_resource[0]].keys() \
                and "group" not in req_details[req_resource[0]].keys():
                logging.error('user or group is required for resources {0} when doing chmod operation '.format(req_resource[0]))
                return False

            if req_details[req_resource[0]]["action"] == "putdata" and "sourcepath" not in req_details[req_resource[0]].keys():
                logging.error('Source path is required for resources {0} when doing putdata operation '.format(req_resource[0]))
                return False

        if req_resource[0].lower() == "service":
            if "name" not in req_details[req_resource[0]].keys() or "action" not in req_details[req_resource[0]].keys():
                logging.error('Resource type {0} missing name or action details in the config file : {1} , please refer document'
                                   .format(req_resource[0], req_details[req_resource[0]].keys()))
                return False

            if req_details[req_resource[0]]["name"] == "" or req_details[req_resource[0]]["name"] == None:
                logging.error('Resource type {0}  name  {1} is not valid in the config file , please refer document'
                                   .format(req_resource[0], req_details[req_resource[0]]["name"]))
                return False
            if req_details[req_resource[0]]["action"] not in ["start", "stop", "restart", "disable", "enable"]:
                logging.error('Resource type {0}  action   {1} is not valid in the config file , please refer document'
                                   .format(req_resource[0], req_details[req_resource[0]]["action"]))
                return False


        # At this point all the configuration is valid
        logging.info("Configuration is valid, will proceed to execute")
        return True

    def __file_operations(self, server_socket, req_details):
        comm = Common()
        if req_details["action"] == "chown":
            status = comm.changefileowner(req_details["path"], req_details["owner"], req_details["group"])
        elif req_details["action"] == "chmod":
            status = comm.changefilePerms(req_details["path"], req_details["mode"])
        elif req_details["action"] == "create":
            status = comm.createfile(req_details["path"])


        return status

    def __service_operations(self, server_socket, req_details):
        pass

    def __pkg_operations(self, server_socket, req_details):
        pass

    def requestprocess(self, server_socket, req_data):
        order_details = sorted([int(i) for i in req_data.keys()])  # To get list of orders
        commonops = Common()
        for order in order_details:
            resource = req_data[str(order)].keys()[0]
            if resource == "pkg":
                status = self.__pkg_operations(server_socket, req_data[str(order)]["pkg"])
            elif resource == "file":
                status = self.__file_operations(server_socket, req_data[str(order)]["file"])
            elif resource == "service":
                status = self.__service_operations(server_socket, req_data[str(order)]["pkg"])

            server_socket.send(str(status).encode()) # send each operation status to the server

            if not status["status"]:
                if "onfailure" in req_data[str(order)][resource].keys():
                    if req_data[str(order)][resource]["onfailure"] == "continue":
                        pass
                    else:
                        return
                else:
                    # menas taking default value to the onfailure and exit from program
                    return




class Common:
    """
    This class mainly impliments varios operating systems tasks using commands or existing python modules.
    """


    def __init__(self):
        pass

    def changefilePerms(self, file, perm):
        """
        :param file: full path of the file
        :param perm:
        :return: Status of the file permissions change operations.
        """
        try:
            if os.path.isfile(file):
                os.chmod(file, perm)
                return {"status": True, "message": "Changed permissions successfully for file {0} to {1}.".format(file, perm)}
            else:
                return {"status": False,
                        "message": "Failed to change permissions. file {0} not exist".format(file)}
        except:
            logging.exception("Faile to set permissions of the file")
            return {"status": False, "message": "Failed to change permissions of file {0} to {1}.".format(file, perm)}

    def changefileowner(self, file, owner, group):
        """
        :param file: file full path
        :param owner: file new owner
        :param group: file new group
        :return: if operation is successful or failure
        """
        try:
            if os.path.isfile(file):
                os.chown(file, owner, group)
                return {"status": True, "message": "Changed owner and group successfully for file {0} to {1}:{2}.".format(file,owner,group)}
            else:
                return {"status": False,
                        "message": "Failed to change owner and group. file {0} not exist".format(file)}
        except:
            logging.exception("Failed to set owner and group of the file")
            return {"status": False, "message": "Failed to change owner and group of file {0} to {1}:{2}.".format(file,owner,group)}

    def createfile(self, filepath):
        """
        :param filename: Full path of the file
        :return: status of operation
        """
        try:
            if not os.path.isfile(filepath):
                fd = open(filepath, "w")
                fd.write("This file is created by cfgmgr")
                fd.close()
                return {"status": True,
                        "message": "Successfully created file".format(filepath)}
        except:
            logging.exception("Failed to create file {0}".format(filepath))
            return {"status": False, "message": "Failed to create file".format(filepath)}

    def changefilecontent(self, file, content):
        """
        :param file: Absolute file path
        :param content: content of the file
        :return: status of the operation
        """
        try:
            with open(file, 'w') as fd1:
                fd1.write(content)
            return "Chaanged the content of the file successfully"
        except:
            print("Error while writing the content to file")
            return "Failed to change the file content"


    def serviceoperation(self, service, operation):
        """
        :param service: Service name to perform action
        :param operation: action to perform on service
        :return status of operation
        """
        if not operation in ('stop', 'start', 'restart'):
            logging.error("Invalid operation to perform on service")
        try:
            os.system("service " + service + " " + operation)
            currentstatus = self.servicestatus(service)
            if 'start' == operation or 'restart' == operation:
                if 'active' == currentstatus:
                    return "successfully started service"
                else:
                    return "Failed to start service"
            else:
                if 'inactive' == currentstatus:
                    return "successfully stopped service"
                else:
                    return "Failed to stop service"
        except:
            logging.error("Failed to perform " + operation + " operation on " + service)

    def servicestatus(self, service):
        """
        :param service:
        :return: Service status
        """
        try:
            p = subprocess.Popen("service " + service + " status | grep -i '   Active' | cut -d' ' -f5", stdout=subprocess.PIPE, shell=True)
            (output, err) = p.communicate()
            return output.decode().rstrip('\n')
        except:
            logging.error("Not able to check the status of the service")


if __name__ == '__main__':
    pass