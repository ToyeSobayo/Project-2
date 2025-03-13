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
                # Return original case for the domain along with its IP.
                mapping[domain.lower()] = (domain, ip)
            else:
                print("Error: Unexpected format", line)
    
    return mapping

def ts1():
    tsDB = loadTsDatabase("../testcases/ts1database.txt")
    print("TS1 database loaded:", tsDB)
    
    # Print the actual hostname and IP of TS1 to verify network configuration.
    actual_hostname = socket.gethostname()
    try:
        actual_ip = socket.gethostbyname(actual_hostname)
    except Exception as e:
        actual_ip = "Unknown"
    print("TS1 running on hostname:", actual_hostname)
    print("TS1 IP address:", actual_ip)
    
    try:
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error as err:
        print("Socket open error:", err)
        sys.exit(1)
    
    serverBinding = ('', port)
    ss.bind(serverBinding)
    ss.listen(5)
    print("TS1 is up on port", port)
    
    print('hi')
    with open("../testcases/ts1responses.txt", "w") as file:
        while True:
            try:
                csockid, addr = ss.accept()
                print("TS1: Got connection from", addr)
                
                request = csockid.recv(1024).decode('utf-8').strip()
                if not request:
                    csockid.close()
                    continue
                
                print("TS1: Received request:", request)
                
                parts = request.split()
                if len(parts) != 4:
                    print("TS1: Invalid request format")
                    csockid.close()
                    continue
                
                domain = parts[1]
                req_id = parts[2]
                
                entry = tsDB.get(domain.lower())
                if entry:
                    og_domain, ip = entry
                    flag = "aa"
                else:
                    og_domain = domain
                    ip = "0.0.0.0"
                    flag = "nx"
                response = f"1 {og_domain} {ip} {req_id} {flag}\n"
                csockid.send(response.encode('utf-8'))
                
                file.write(response)
                file.flush()
                
                csockid.close()
            except socket.error as e:
                print("TS1 socket error:", e)
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
    
    ts1()
