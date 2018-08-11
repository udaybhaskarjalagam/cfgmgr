import os, subprocess

class Common:

    def __init__(self):
        pass

    def changefilePerms(self, file, perm):
        """
        :param file:
        :param perm:
        :return: Status of the file permissions change operations.
        """
        try:
            os.chmod(file, perm)
            return "Changed permissions successfully."
        except:
            print("Faile to set permissions of the file")
            return "Failed to change permissions."

    def changefilecontent(self, file, content):
        """
        :param file: Absolute file path
        :param content: content of the file
        :return:
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
        :param service:
        :param operation:
        :return status of operation:
        """
        if not operation in ('stop', 'start', 'restart'):
            print("Invalid operation to perform on service")
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
            print("Failed to perform " + operation + " operation on " + service)

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
            print("Not able to check the status of the service")


if __name__ == '__main__':
    pass