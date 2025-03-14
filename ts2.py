import sys
import socket

def loadTsDatabase(filename):
    mapping = {}
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) == 2:
                domain, ip = parts
                mapping[domain.lower()] = (domain, ip)
            else:
                print("Error: Unexpected format", line)
    
    return mapping

def ts2():
    tsDB = loadTsDatabase("ts2database.txt")
    print("ts2 db loaded:", tsDB)

    try:
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error as err:
        print("Socket open error:", err)
        sys.exit(1)

    serverBinding = ('', port)
    ss.bind(serverBinding)
    ss.listen(5)
    print("ts2 up on port", port)

    with open("ts2responses.txt", "w") as file:
        while True:
            try:
                csockid, addr = ss.accept()
                print("ts2: Got connection from", addr)

                request = csockid.recv(1024).decode('utf-8').strip()
                if not request:
                    csockid.close()
                    continue

                print("ts2: request:", request)

                parts = request.split()
                if len(parts) != 4:
                    print("ts2: invalid request format")
                    csockid.close()
                    continue
                
                domain = parts[1]
                reqId = parts[2]

                entry = tsDB.get(domain.lower())
                if entry:
                    originalDomain, ip = entry
                    flag = "aa"
                else:
                    originalDomain = domain
                    ip = "0.0.0.0"
                    flag = "nx"
                response = f"1 {originalDomain} {ip} {reqId} {flag}\n"
                csockid.send(response.encode('utf-8'))

                file.write(response)
                file.flush()

                csockid.close()
            except socket.error as e:
                print("ts2 socket error:", e)
                break
    ss.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 {} <rudns_port>".format(sys.argv[0]))
        sys.exit(1)
    
    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Invalid port number")
        sys.exit(1)

    ts2()
