#! /usr/bin/env python3

import sys
sys.path.append("../lib")       # for params
import re, socket, params, os

switchesVarDefaults = (
        (('-l', '--listenPort') ,'listenPort', 50001),
        (('-d', '--debug'), "debug", False), # boolean (set if present)
        (('-?', '--usage'), "usage", False), # boolean (set if present)
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

while True:
    sock, addr = lsock.accept()

    from framedSock import framedSend, framedReceive

    if not os.fork():
        fileinformation = ((framedReceive(sock,debug)).decode()
        print("Received the file information" , fileinformation)
        filename, filesize, remotefilename = fileinformation.split(":")
        filesize = int(filesize)

        #Checking if the file existed already
        path = os.getcwd()+"/"+remotefilename

        if os.path.exits(path) is True:
           print("The server already contain this file")
           framedSend(sock, framedReceive(sock, debug), debug)

        else:
         print("new child process handling connection from", addr)
         with open (remoteFilename, "w") as f:
            print("Received file data")
            payload = framedReceive(sock, debug)

            #Payload gets decoded and written to the remote file if it is not none
            #Otherwise it does nothing
            if payload is not None:
               payloadDecoded = payload.decode()
               f.write(payloadDecoded)
               framedSend(sock, payload, debug)
    else:
        sock.close()
