#!/bin/bash
#set -x

echo "Inistialization started"
PYTHON=""
if [ -x "$(command -v python)" ]; then
    PYTHON=`command -v python`
elif [ -x "$(command -v python3)" ]; then
    PYTHON=`command -v python3`
fi

if [ "$PYTHON" = "" ]; then
   echo "Python not found, will install python"
   if [ -x "$(command -v apt-get)" ]; then
        apt-get -qq -y install python3
   else
        yum -d1 -y install python3
   fi
   PYTHON=`command -v python3`
fi

if  [ "$PYTHON" = "" ]; then
    echo "Not able to find python to execute the program"
else
    echo "$PYTHON found , will use it to run cfgmgr"
fi

if [ "$1" = "client" ]; then
    nohup $PYTHON client.py &
elif [ "$1" = "server" ]; then
    echo "All set to use server"
    $PYTHON server.py -h
else
    echo "Unknown option $1"
    echo "usage :  bootstrap.sh <server|client>"
fi
