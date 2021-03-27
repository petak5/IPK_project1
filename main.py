#!/usr/local/bin/python3
# File: main.py
# Date: 26. 3. 2021
# Author: Peter Uroš (xurgos00)
# Brief: IPK project 1

import os
import sys
import re
from urllib.parse import urlparse
from socket import *


def main():

    if len(sys.argv) != 5:
        invalidArguments()

    # Parse arguments
    nameserver, fileserver = parseArguments()

    # Validate nameserver address
    if not re.match('^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?):[0-9]{1,5}$', nameserver):
        print("Invalid nameserver address.")
        exit(1)

    # Validate filserver URL
    fileserverURL = urlparse(fileserver)
    if fileserverURL.hostname == "" or fileserverURL.path == "" or fileserverURL.scheme != "fsp":
        print("Invalid fileserver URL.")
        exit(1)

    # Ask nameserver for the IP of fileserver
    fileserverAddress = getFileserverAddress(nameserver, fileserverURL.hostname)

    # Connect to fileserver
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.settimeout(10)
    clientSocket.connect(fileserverAddress)

    # Receive file content
    file_content = fileserverGetFileContents(clientSocket, fileserverURL.hostname, fileserverURL.path)

    # Write data to file
    os.makedirs(os.path.dirname("." + fileserverURL.path), exist_ok=True)
    f = open("." + fileserverURL.path, "wb")
    f.write(file_content)

    clientSocket.close()


"""Argument nameserver contains nameserver IP and port separated with ":"
Argument fileserverHostname is fileserver's hostname
Returns tuple of fileserver IP and port"""
def getFileserverAddress(nameserver: str, fileserverHostname: str):
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.settimeout(5)
    message = ('WHEREIS ' + fileserverHostname).encode()
    nameserverIP, nameserverPort = nameserver.split(':')
    clientSocket.sendto(message, (nameserverIP, int(nameserverPort)))
    receivedMessage, _ = clientSocket.recvfrom(2048)
    clientSocket.close()

    if not str(receivedMessage).startswith("b'OK"):
        print("Failed to acquire fileserver address from DNS")
        exit(1)

    # Parse filserver IP and port from response
    fileserverIPWithPort = str(receivedMessage)[5:-1].split(":")
    fileserverAddress = (fileserverIPWithPort[0], int(fileserverIPWithPort[1]))

    return fileserverAddress


"""Argument socket is client configured socket connected to fileserver
Argument hostname is fileserver hostname
Argument filePath is path to file on fileserver
Returns bytearray containing file contents
"""
def fileserverGetFileContents(socket: socket, hostname: str, filePath: str):
    # Send request to fileserver
    socket.send(("GET " + filePath + " FSP/1.0\r\n").encode())
    socket.send(("Hostname: " + hostname + "\r\n").encode())
    socket.send(("Agent: xurgos00\r\n").encode())
    socket.send(("\r\n").encode())
    # Receive response
    response = bytearray()
    while True:
        r = socket.recv(32)
        if not r:
            break
        response.extend(r)

    response_str = str(response)[12:-2]
    if not response_str.startswith("FSP/1.0 Success"):
        print("Failed to receive file from fileserver")
        exit(1)

    # Get length of data segment
    response_header = response_str.split("\\r\\n", 4)[0: -1]
    response_data_length = int(response_header[1].split(":")[1])

    return response[-response_data_length:]


def parseArguments():
    nameserver = ""
    fileserver = ""

    # Parse arguments
    if sys.argv[1] == "-n":
        nameserver = sys.argv[2]
        if sys.argv[3] == "-f":
            fileserver = sys.argv[4]
        else:
            invalidArguments()
    elif sys.argv[1] == "-f":
        fileserver = sys.argv[2]
        if sys.argv[3] == "-n":
            nameserver = sys.argv[4]
        else:
            invalidArguments()
    else:
        invalidArguments()

    return nameserver, fileserver


def invalidArguments():
    print("Invalid arguments.")
    exit(1)


if __name__ == '__main__':
    main()
