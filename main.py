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
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.settimeout(5)
    message = ('WHEREIS ' + fileserverURL.hostname).encode()
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

    # Connect to fileserver
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.settimeout(10)
    clientSocket.connect(fileserverAddress)

    # Send request to fileserver
    clientSocket.send(("GET " + fileserverURL.path + " FSP/1.0\r\n").encode())
    clientSocket.send(("Hostname: " + fileserverURL.hostname + "\r\n").encode())
    clientSocket.send(("Agent: xurgos00\r\n").encode())
    clientSocket.send(("\r\n").encode())
    # Receive response
    response = bytearray()
    while True:
        r = clientSocket.recv(32)
        if not r:
            break
        response.extend(r)

    clientSocket.close()

    response_str = str(response)[12:-2]
    if not response_str.startswith("FSP/1.0 Success"):
        print("Failed to receive file from fileserver")
        exit(1)

    # Get length of data segment
    response_header = response_str.split("\\r\\n", 4)[0: -1]
    response_data_length = int(response_header[1].split(":")[1])

    # Write data to file
    os.makedirs(os.path.dirname("." + fileserverURL.path), exist_ok=True)
    f = open("." + fileserverURL.path, "wb")
    f.write(response[-response_data_length:])

def invalidArguments():
    print("Invalid arguments.")
    exit(1)

if __name__ == '__main__':
    main()
