import sys
import socket

def loadRsDatabase(filename):
    tldMap = {}
    directMap = {}

    with open(filename, 'r') as f:
        lines = f.readlines()
    
    if len(lines) < 2:
        raise Exception("file must have at least two lines for TDL mappin")

    ts1Line = lines[0].strip()
    ts2Line = lines[1].strip()

    ts1Parts = ts1Line.split()
    ts2Parts = ts2Line.split()

    if len(ts1Parts) != 2 or len(ts1Parts) != 2:
        raise Exception("First two lines must contain *exactly* two values")
    
    tldMap['ts1'] = (ts1Parts[0].lower(), ts1Parts[1])
    tldMap['ts2'] = (ts2Parts[0].lower(), ts2Parts[1])

    for line in lines[2:]:
        line = line.strip()

        if line == "":
            continue
        parts = line.split()
        if len(parts) == 2:
            domain, ip = parts
            directMap[domain.lower()] = ip
        else:
            print("Error: Unexpeced format", line)
    
    return tldMap, directMap
def server():

    try:
        tldMap, directMap = loadRsDatabase("../testcases/rsdatabase.txt")
    except Exception as e:
        print("Error loading RS database", e)
        sys.exit(1)
    
    print("Server is running on port", port)
    print("TLD Mapping", tldMap)
    print("Direct Mapping", directMap)

    try:
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error as err:
        print("Socket open error:", err)
        sys.exit(1)

    serverBinding = ('', port)
    ss.bind(serverBinding)
    ss.listen(5)
    print("Listening on port", port)

    csockid, addr = ss.accept()
    print("Connection from", addr)

    test = "1 test.domain.com 127.0.0.1 1 aa\n"
    csockid.send(test.encode('utf-8'))

    csockid.close()
    ss.close()
    

    print("Server is up and running on port", port)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 {} <rudns_port>".format(sys.argv[0]))
        sys.exit(1)
    
    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Invalid port number")
        sys.exit(1)

    server()