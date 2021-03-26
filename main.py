# File: main.py
# Date: 26. 3. 2021
# Author: Peter Uroš (xurgos00)
# Brief: IPK project 1

import sys
import re
from urllib.parse import urlparse


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

    if not re.match('^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?):[0-9]{1,5}$', nameserver):
        print("Invalid nameserver address.")
        exit(1)

    fileserverURL = urlparse(fileserver)
    if fileserverURL.path == "" or fileserverURL.scheme != "fsp":
        print("Invalid fileserver URL.")
        exit(1)

    print("NS: " + nameserver)
    print("FS: " + fileserver)

def invalidArguments():
    print("Invalid arguments.")
    exit(1)

if __name__ == '__main__':
    main()
