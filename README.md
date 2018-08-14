# Configuration manager 
Basic configuration manger tool to perform some operations on multiple remote servers. Check the runconfig file to check the operations you can perform using this configuration manager.

Architecture : 

![alt text](https://github.com/udaybhaskarjalagam/cfgmgr/blob/master/cfgmgr.png)

`How to initialize :`
   
   To initialize the tool, download the code from github as zip or cloning it using git.
   
   git clone https://github.com/udaybhaskarjalagam/cfgmgr.git
   
   folder structure should looks like this. 
   
   - cfgmgr 
        - bootstrap.sh
        - client.py
        - server
        - lib (folder)
              - common.py
        - log (folder) 
        - cfg (folder) : runactions.json  and clientcfg.json
        
   First thing after downloading code is change bootstrap.sh mode to executable and run it with as as shown below.
    
   usage :  bootstrap.sh <server|client>
   
   It will verify if java exist and install if not , if you run it with client option it will start client process as demon in backend. 
   
    
`How to start client :`


On all the clients you want to use this config mgr run below command , it will start client in demon mode , for simplicity port 9966 is hardcoded. the port should be unused for client to start. or you can change code to use different port.  

_bootstrap.sh client_ 


`How to use config manager :`

There are couple of things need to know before using the tool. 

**clientcfg.json** : (fixed path ./cfg/clientcfg.json) Below is the example of how to use clientcfg, this file is used to define client groups so you can run on multiple clients  at a time.
 
```json
{ "groups":
  {
   "group1":[
              "host1"
            ],
   "group2":[
              "host1",
              "host2"
   ]
  }
}
```

**runactions.json** : (default ./cfg/runactions.json) Below is syntax of runactions.json file where you define what actions you want to perform on clients.
 
```json
{
    "1": {
      // Sequence number to decide the order of execution
      "pkg": {
        // which package to perform the action on
        "names": "packagename",
        // what actions to perform on the above package, expected install, remove or installstatus
        "action": "install",
        // What to do when action fails expected values   stop, continue
        "onfailure": "stop"
      }
    },
    "2": {
      "file": {
        //Remote path to perform operations on
        "path": "/tmp/temp.txt",
        // actions on the file to perform , expected   chmod, chown , create, remove, write  (note: put data will also create file if not exist and replace if exist)
        "action": "create",
        // Currently support changing only file basic permissions for user, group and others give 3 digit appropriate nubber
        "mode": "777",
        // required if action is chown
        "owner": "root",
        // required if action is chown
        "group": "root",
        //This is mandatory if action is putdata
        "sourcepath": "/tmp/src.txt",
        // What to do when action fails expected values   stop, continue
        "onfailure": "stop"
      }
    },

    "3": {
    "service": {
      // name of the service
      "name": "httpd",
      // action to perform on respective service expected    (start, stop, restart )
      "action": "start",
      // What to do when action fails expected values   stop, continue
      "onfailure": "stop"
    }
  }
}


```


To understand the above json file : 
- fist key in the file define the sequence , and each sequence expected to have only one task.
and execution is performed in the sequence. 
- second level is the resource type (Currently support only 3 resources , pkg, file and service)
- Each resource have have multiple keys as shown above, some are mandatory. 

This is mandatory file required to execute the server.

```text
root@master:~/python/cfgmgr# python3 server.py -h
usage: server.py [-h] (-c CLIENTS [CLIENTS ...] | -g GROUPS [GROUPS ...])
                 [-a ACTIONS]

config manger tool to perform operations on remote servers

optional arguments:
  -h, --help            show this help message and exit
  -c CLIENTS [CLIENTS ...], --clients CLIENTS [CLIENTS ...]
                        List of Clients seperated by space to perform actions
  -g GROUPS [GROUPS ...], --groups GROUPS [GROUPS ...]
                        List of Groups seperated by space to perform actions
  -a ACTIONS, --actions ACTIONS
                        Configuration files to perform actions on the clients,
                        this is json file
```





below are few examples you can use.

```text
python3 server.py -c 192.168.1.101 192.168.1.102 192.168.1.103 192.168.1.104

python3 server.py -g group1 group2

python3 server1 -g group1 -a ./cfg/clientcfg.json      # ./cfg/clientcfg.json  is default file it looks for if not given.

```



example of how output looks like . 

```text

root@master:~/python/cfgmgr# python3 server.py -c 192.168.1.106 192.168.1.101
2018-08-13 20:43:28,359 : INFO : Configuration is valid, will proceed to execute
2018-08-13 20:43:30,105 : INFO : 192.168.1.106: {'status': 'successful', 'message': 'Successfully installed apache2 package'}
2018-08-13 20:43:31,088 : INFO : 192.168.1.101: {'status': 'successful', 'message': 'Successfully installed apache2 package'}
2018-08-13 20:43:31,731 : INFO : 192.168.1.106: {'status': 'successful', 'message': 'Successfully installed php package'}
2018-08-13 20:43:31,739 : INFO : 192.168.1.106: {'status': 'Success', 'message': 'Successfully renamed the file from /var/www/html/index.html to /var/www/html/index.back'}
2018-08-13 20:43:31,747 : INFO : 192.168.1.106: {'status': 'Failed', 'message': 'File already exist'}
2018-08-13 20:43:31,748 : INFO : 192.168.1.106: {'status': 'Success', 'message': 'Changed permissions successfully for file /var/www/html/index.php to 644.'}{'status': 'Success', 'message': 'Changed owner and group successfully for file /var/www/html/index.php to root:root.'}
2018-08-13 20:43:31,802 : INFO : 192.168.1.106: {'status': 'Success', 'message': 'successfully started service apache2'}
2018-08-13 20:43:32,766 : INFO : 192.168.1.106: {'status': 'Success', 'message': 'successfully enabled service apache2'}
2018-08-13 20:43:32,766 : INFO : 192.168.1.106: Request process completed
2018-08-13 20:43:33,886 : INFO : 192.168.1.101: {'status': 'successful', 'message': 'Successfully installed php package'}
2018-08-13 20:43:33,892 : INFO : 192.168.1.101: {'status': 'Success', 'message': 'Successfully renamed the file from /var/www/html/index.html to /var/www/html/index.back'}
2018-08-13 20:43:33,898 : INFO : 192.168.1.101: {'status': 'Failed', 'message': 'File already exist'}
2018-08-13 20:43:33,899 : INFO : 192.168.1.101: {'status': 'Success', 'message': 'Changed permissions successfully for file /var/www/html/index.php to 644.'}{'status': 'Success', 'message': 'Changed owner and group successfully for file /var/www/html/index.php to root:root.'}
2018-08-13 20:43:33,961 : INFO : 192.168.1.101: {'status': 'Success', 'message': 'successfully started service apache2'}
2018-08-13 20:43:35,392 : INFO : 192.168.1.101: {'status': 'Success', 'message': 'successfully enabled service apache2'}
2018-08-13 20:43:35,393 : INFO : 192.168.1.101: Request process completed

```


