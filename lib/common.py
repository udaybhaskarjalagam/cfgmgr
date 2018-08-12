import os, subprocess
import pwd, grp
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='./client.log',level=logging.INFO)

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
            if req_details[req_resource[0]]["action"] not in ["chmod", "chown", "create", "remove", "write"]:
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

            if req_details[req_resource[0]]["action"] == "write" and "sourcepath" not in req_details[req_resource[0]].keys():
                logging.error('Source path is required for resources {0} when doing write operation '.format(req_resource[0]))
                return False

            if req_details[req_resource[0]]["action"] == "write" and "sourcepath" in req_details[req_resource[0]].keys():
                if not os.path.isfile( req_details[req_resource[0]]["sourcepath"]):
                    logging.error('Source file {0} does not exist for resources {0} for doing write operation '
                                  .format(req_details[req_resource[0]]["sourcepath"], req_resource[0]))
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
            if "mode" in req_details.keys() :
                server_socket.send(str(status).encode())
                status= comm.changefilePerms(req_details["path"], req_details["mode"] )
            if "owner" in req_details.keys() and "group" in req_details.keys():
                server_socket.send(str(status).encode())
                status = comm.changefileowner(req_details["path"], req_details["owner"], req_details["group"])
            if "data" in req_details.keys():
                status = comm.changefilecontent(req_details["path"], req_details["data"])
        elif req_details["action"] == "write":
            status = comm.changefilecontent(req_details["path"], req_details["data"])
        return status

    def __service_operations(self, server_socket, req_details):
        comm = Common()
        status = comm.service_operation(req_details["name"], req_details["action"])
        return status

    def __pkg_operations(self, server_socket, req_details):
        """
        This mentod will check action type of the pacakge resources and call appropriate mentod
        :param server_socket: server socket if need to send message to server directly
        :param req_details: ALl the details required for the operation on pacakges
        :return: dict object contains status of the operations
        """
        comm = Common()
        if req_details["action"] == "install":
            status = comm.package_install(req_details["name"])
        elif  req_details["action"] == "remove":
            status = comm.package_remove(req_details["name"])
        elif req_details["action"] == "installstatus":
            status = {"status": "Underconstruction", "message": "service under construction"}

        return status


    def requestprocess(self, server_socket, req_data):
        order_details = sorted([int(i) for i in req_data.keys()])  # To get list of orders
        commonops = Common()
        for order in order_details:
            try:
                resource = list(req_data[str(order)].keys())[0]
                if resource == "pkg":
                    status = self.__pkg_operations(server_socket, req_data[str(order)]["pkg"])
                elif resource == "file":
                    status = self.__file_operations(server_socket, req_data[str(order)]["file"])
                elif resource == "service":
                    status = self.__service_operations(server_socket, req_data[str(order)]["service"])

                server_socket.send(str(status).encode()) # send each operation status to the server
            except:
                server_socket.send("Error while processing oder number {0} for {1} resource".format(order, resource).encode())
                logging.exception("Error while processing requests")

            if status["status"] == "Failed":
                if "onfailure" in req_data[str(order)][resource].keys():
                    if req_data[str(order)][resource]["onfailure"] == "continue":
                        server_socket.send(
                            "Error while processing oder number {0} for {1} resource".format(order, resource).encode())
                        server_socket.send(
                            "Will continue because of onfailure option is set to continue")
                    else:
                        server_socket.send(
                            "Exiting from program becasue {0} order failed and onfailure not set to continue"
                                .format(order).encode())
                        return
                else:
                    # menas taking default value to the onfailure and exit from program
                    server_socket.send("Exiting from program becasue {0} order failed and onfailure not set to continue"
                                       .format(order).encode())


class Common:
    """
    This class mainly implements various operating systems tasks using commands or existing python modules.
    """


    def __init__(self):
        self.pkgmgr = self.__get_pkgmgr()

    def changefilePerms(self, file, perm):
        """
        :param file: full path of the file
        :param perm:
        :return: Status of the file permissions change operations.
        """
        try:
            if os.path.isfile(file):
                os.chmod(file, perm)
                return {"status": "Success", "message": "Changed permissions successfully for file {0} to {1}."
                    .format(file, perm)}
            else:
                return {"status": "Failed",
                        "message": "Failed to change permissions. file {0} not exist".format(file)}
        except:
            logging.exception("Faile to set permissions of the file")
            return {"status": "Failed", "message": "Failed to change permissions of file {0} to {1}."
                .format(file, int(perm))}

    def changefileowner(self, file, owner, group):
        """
        :param file: file full path
        :param owner: file new owner
        :param group: file new group
        :return: if operation is successful or failure
        """
        try:
            if os.path.isfile(file):
                uid = pwd.getpwnam("nobody").pw_uid
                gid = grp.getgrnam("nogroup").gr_gid
                os.chown(file, uid, gid)
                return {"status": "Success", "message": "Changed owner and group successfully for file {0} to {1}:{2}.".format(file,owner,group)}
            else:
                return {"status": "Failed",
                        "message": "Failed to change owner and group. file {0} not exist".format(file)}
        except:
            logging.exception("Failed to set owner and group of the file")
            return {"status": "Failed", "message": "Failed to change owner and group of file {0} to {1}:{2}.".format(file,owner,group)}

    def createfile(self, filepath):
        """
        :param filename: Full path of the file
        :return: status of operation
        """
        try:
            if not os.path.isfile(filepath):
                fd = open(filepath, "w")
                fd.write("This file is created by cfgmgr\n")
                fd.close()
                return {"status": "Success", "message": "Successfully created file".format(filepath)}
            else:
                return {"status": "Failed",
                        "message": "File already exist".format(filepath)}
        except:
            logging.exception("Failed to create file {0}".format(filepath))
            return {"status": "Failed", "message": "Failed to create file".format(filepath)}

    def changefilecontent(self, file, content):
        """
        :param file: Absolute file path
        :param content: content of the file
        :return: status of the operation
        """
        try:
            with open(file, 'w') as fd1:
                fd1.write(content)
                return {"status": "Success", "message": "Successfully written data to file {0}".format(file)}
        except:
            logging.exception("Error while writing the content to file")
            return {"status": "Failed", "message": "Failed change content of the file {0}".format(file)}

    def service_operation(self, service, operation):
        """
        :param service: Service name to perform action
        :param operation: action to perform on service
        :return status of operation
        """
        if not operation in ('stop', 'start', 'restart', 'status'):
            logging.error("Invalid operation to perform on service")
        try:
            os.system("systemctl " + operation + " " + service )
            currentstatus = self.service_status(service)
            enable_status = self.service_enabled(service)
            if 'start' == operation or 'restart' == operation:
                if 'active' == currentstatus:
                    return {"status": "Success", "message": "successfully started service {0}".format(service)}
                else:
                    return {"status": "Failed", "message": "Failed to start service {0}".format(service)}
            elif 'stop' == operation :
                if 'inactive' == currentstatus:
                    return {"status": "Success", "message": "successfully stopped service {0}".format(service)}
                else:
                    return {"status": "Failed", "message": "failed to stop service {0}".format(service)}
            elif 'enable' == operation :
                if enable_status != "Failed":
                    if enable_status:
                        return {"status": "Success", "message": "successfully enabled service {0}".format(service)}
                    else:
                        return {"status": "Failed", "message": "failed to enable service {0}".format(service)}
                else:
                    return {"status": "Failed", "message": "failed to enable service {0}".format(service)}
            elif 'disable' == operation :
                if enable_status != "Failed":
                    if not enable_status:
                        return {"status": "Success", "message": "successfully disabled service {0}".format(service)}
                    else:
                        return {"status": "Failed", "message": "failed to disabled service {0}".format(service)}
                else:
                    return {"status": "Failed", "message": "failed to disabled service {0}".format(service)}

        except:
            return {"status": "Failed", "message": "failed to {0} service {1}".format(operation, service)}
            logging.error("Failed to perform " + operation + " operation on " + service)

    def service_enabled(self, service):
        """
        :param service:
        :return: return if service enabled or not
        """
        try:
            p = subprocess.Popen("systemctl status" + service + "  | grep -i '   Loaded' | cut -d';' -f2", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            (output, err) = p.communicate()
            status = output.decode().rstrip('\n')
            status = status.lstrip()
            if status == "enabled":
                return True
            else:
                return False
        except:
            return "Failed"
            logging.error("Not able to check the status of the service")

    def service_status(self, service):
        """
        :param service:
        :return: Service status
        """
        try:
            p = subprocess.Popen("systemctl status" + service + "  | grep -i '   Active' | cut -d' ' -f5", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            (output, err) = p.communicate()
            return output.decode().rstrip('\n')
        except:
            logging.error("Not able to check the status of the service")

    def package_install(self, pkgname):
        """
        This method to install any pacakges using yum or
        :param pkgname:
        :return:
        """
        if self.pkgmgr == 'apt':
            self.runcommand('apt-get -y install '+ pkgname)
        else:
            self.runcommand('yum -y install ' + pkgname)

        if self.checkifpackageinstalled(pkgname):
            return {"status": "successful", "message": "Successfully installed {0} package".format(pkgname)}
        else:
            return {"status": "Failed", "message": "Failed to install {0} package".format(pkgname)}

    def package_remove(self, pkgname):
        """
        This method to remove  any pacakges using yum or apt
        :param pkgname:
        :return: Resturn status of pkg removed
        """
        if self.pkgmgr == 'apt':
            self.runcommand('remove -y remove '+ pkgname)
        else:
            self.runcommand('yum -y remove ' + pkgname)

        if not self.checkifpackageinstalled(pkgname):
            return {"status": "successful", "message": "Successfully installed {0} package".format(pkgname)}
        else:
            return {"status": "Failed", "message": "Failed to install {0} package".format(pkgname)}

    def __get_pkgmgr(self):
        """
        :return: return which pkgmgr to use when running the commands
        """
        (output, error) = self.runcommand('command -v apt-get')
        if output:
            return 'apt'
        else:
            return 'yum'

    def checkifpackageinstalled(self, pkgname):
        """
        :param pkgname: name of the package to check if installed
        :return: if package is installed
        """
        if self.pkgmgr == "apt":
            (output, err) =self.runcommand('apt list --installed | grep -i ' + pkgname +' | cut -d"/" -f1')
            if output:
                list_of_services = output.decode().split('\n')
                if pkgname in list_of_services:
                    return True
                else:
                    return False
            else:
                return False
        else:
            # Will be replacing with yum later
            (output, err) = self.runcommand('yum list installed ' + pkgname +'| grep -i ' + pkgname + ' | cut -d"/" -f1')

    def runcommand(self, command):
        """
        :param command: full command to run on the remote server
        :return: command output will be returned.
        """
        try:
            p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            (output, err) = p.communicate()
            return (output, err)
        except:
            return ("Error While running the command\n".encode(), "Error while runnning the command\n".encode())
            logging.exception("Not able to check the status of the service")



if __name__ == '__main__':
    pass