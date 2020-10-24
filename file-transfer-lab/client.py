#! /usr/bin/env python3
# Echo client program
import socket, sys, re

sys.path.append("../lib")       # for params
import params

from framedSock import framedSend, framedReceive

filename = ""
switchesVarDefaults = (
        (('-s', '--server'), 'server', "127.0.0.1:50001"),
        (('-d', '--debug'), "debug", False), # boolean (set if present)
        (('-?', '--usage'), "usage", False), # boolean (set if present)
        )




progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]

if usage:
        params.usage()

try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)

except:

    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

filename = input("Enter the file name from the client: ")
remotefilename = input("Enter the remote name for the server: ")
separation = ":"


addrFamily = socket.AF_INET
socktype = socket.SOCK_STREAM
addrPort = (serverHost, serverPort)

s = socket.socket(addrFamily, socktype)

if s is None:
    print('could not open socket')
    sys.exit(1)

s.connect(addrPort)

try:
    filesize = os.path.getsize(filename)

    if filesize == 0:
        print("The file is empty")
        sys.exit(0)
    print("Sending the file's name, size, and remote file name ")
    framedSend(s, f"{filename}{separation}{filesize}{separation}{remotefilename}".encode(), debug)

    stuff = " "

    with open(filename, "r") as a:
        for data in filename:
            data = a.read()

            if not data:
                break
            else:
                stuff = data.encode()

        print("Sending file data")
        framedSend(s,stuff,debug)

    print("Received: ", framedReceive(s, debug))
except FileNotFoundError as e:
    print("There is not such file")
    sys.exit(0) 
