import sys
import socket

def client():

    print("Client connecting to server", rsHostName, "on port: ", port)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 {} <rsHostName> <rudns_port>".format(sys.argv[0]))
        sys.exit(1)
    
    rsHostName = sys.argv[1]
    try:
        port = int(sys.argv[2])
    except ValueError:
        print("Invalid port number")
        sys.exit(1)

    client()