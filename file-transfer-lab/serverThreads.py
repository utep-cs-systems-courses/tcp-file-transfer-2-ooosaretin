#! /usr/bin/env python3

import sys
sys.path.append("../lib")       # for params
import re, socket, params, os

switchesVarDefaults = (
    (('-l', '--listenPort'), 'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)

from threading import Thread;
from encapFramedSock import EncapFramedSock
import threading

global fileBeingTransferred
global lock

filesBeingTransferred = []
lock = threading.Lock()

#Checks if the file is already being transferred to
def fileTransferStart(filename):
    if filename in filesBeingTransferred:
        return True
    else:
        filesBeingTransferred.append(filename)
        return False

#Removes file after transfer is done
def fileTransferEnd(filename):
    fileBeingTransferred.remove(filename)

class Server(Thread):
    def __init__(self, sockAddr):
        Thread.__init__(self)
        self.sock, self.addr = sockAddr
        self.fsock = EncapFramedSock(sockAddr)
    def run(self):
        print("new thread handling connection from", self.addr)
        filename = (self.fsock.receive(debug)).decode()
        print("\nFile is being checked for transfer status")

        if fileTransferStart(filename) is True:
            msg = "Waiting"
            msg = msg.encode()
            self.fsock.send(msg,debug)
            print("\nFile is currently being transferred - Please Wait")
            lock.aquire()
            msg = "ready for Transfer"
            msg = msg.encode()
            self.fsock.send(msg,debug)
            filesBeingTransferred.append(filename)
            print("\nThread", threading.current_thread(), "lock was acquired")

        else:
            msg = "Ready for transfer"
            msg = msg.encode()
            self.fsock.send(msg, debug)
            print("\nFile is not currently being transferred")
            lock.acquire()
            print("\nThread ", threading.current_thread(), "lock was acquired")

        serverfilename = (self.fsock.receive(debug)).decode()
        print("\nThe server file's name was received")

        #checks if the file already exit on server
        path = os.getcwd()+"/"+serverfilename

        if os.path.exits(path) is True:
            print("\nThe file is already on the server")
            payload = self.fsock.receive(debug)
            self.fsock.send(payload, debug)

        else:
            with open(serverfilename, "w") as f:
                print("\nFile data is being recieved...")
                payload = self.fsock.receive(debug)

                #Decodes payload if it is not none and writes to the remote file
                #If payload is nothing is none then it writes nothing to the remote file

                if payload is not None:
                    payloadDecoded = payload.decode()
                    f.write(payloadDecoded)
                    self.fsock.send(payload, debug)
                    lsock.release()
                    print("\nThread ", threading.current_thread(), "lock was released")
                    fileTransferEnd(filename)
                    print("\nExisting......")


while True:
    sockAddr = lsock.accept()
    server = server(sockAddr)
    server.start()
