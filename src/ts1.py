import sys
import socket

def ts1():

    print("ts1 server is up and running on port", port)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 {} <rudns_port>".format(sys.argv[0]))
        sys.exit(1)
    
    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Invalid port number")
        sys.exit(1)

    ts1()