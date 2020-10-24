#! /usr/bin/env python3

# Echo client program
import socket, sys, re, os

sys.path.append("../lib")       # for params
import params

from encapFramedSock import EncapFramedSock

switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

programe = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug = paramMap["server"], paramMap["usage"], paramMap["debug"]

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

sock = socket.socket(addrFamily, socktype)

if sock is None:
    print('could not open socket')
    sys.exit(1)

sock.connect(addrPort)

fsock = EncapFramedSock((sock, addrPort))

try:
    filesize = os.path.getsize(filename)
    if filesize == 0:
        print("\nThere's nothing in the file")
        sys.exit(0)

    fsock.send(f"{filename}".encode(), debug)
    print("\n File name was sent to be checked to see if it was being transferred\n")
    status = (fsock.receive(debug)).decode()
    print("\n File transfer status: ", status)

    if status == "Waiting":
        while True:
            status = (fsock.receive(debug)).decode()
            if status is not "Waiting":
                break

    prompt = "\nStatus is ready - Press enter to continue."
    i = input(prompt)
    serverfilename = remotefilename.encode()

    print("\nThe server file name was sent")
    fsock.send(serverfilename, debug)

    stuff = ""
    with open(filename, "r") as a:
        for data in filename:
            data = a.read()
            if not data:
                break
            else:
                stuff = data.encode()
                print("\nFile data is being sent...")
                fsock.send(stuff,debug)

    print("\nFile data was sent back to the client")
    fsock.receive(debug)

except FileNotFoundError as e:
    print("\nThe file doesn't exist")
    sys.exit(0)
