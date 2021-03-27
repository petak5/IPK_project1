# File: main.py
# Date: 26. 3. 2021
# Author: Peter Uroš (xurgos00)
# Brief: IPK project 1

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
    message = ('WHEREIS ' + fileserverURL.hostname).encode('unicode_escape')
    nameserverAddress, nameserverPort = nameserver.split(':')
    clientSocket.sendto(message, (nameserverAddress, int(nameserverPort)))
    receivedMessage, fileserverAddress = clientSocket.recvfrom(2048)
    clientSocket.close()

    if not str(receivedMessage).startswith("b'OK"):
        print("Failed to acquire fileserver address from DNS")
        exit(1)

    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect(fileserverAddress)

    print("NS: " + nameserver)
    print("FS: " + fileserver)

def invalidArguments():
    print("Invalid arguments.")
    exit(1)

if __name__ == '__main__':
    main()
