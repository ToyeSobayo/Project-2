import sys
import socket

def client():
    try:
        with open('hostnames.txt', 'r') as file:
            hostnames = file.read().strip().split('\n')
    except FileNotFoundError:
        print("hostnames.txt not found")
        sys.exit(1)
    
    with open('resolved.txt', 'w') as output:
        idNum = 1
        
        for line in hostnames:
            parts = line.strip().split()
            if len(parts) != 2:
                print(f"Invalid format in hostnames.txt: {line}")
                continue
            hostname, flag = parts
            
            request = f"0 {hostname} {idNum} {flag}\n"
            
            try:
                rsSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                rsSocket.connect((rsHostName, port))
                rsSocket.send(request.encode('utf-8'))
                
                response = rsSocket.recv(1024).decode('utf-8').strip()
                rsSocket.close()
                
                resParts = response.split()
                if len(resParts) != 5:
                    print(f"Invalid response format: {response}")
                    continue
                    
                resType, domain, ip, resId, resFlag = resParts
                
                output.write(f"{response}\n")
                output.flush()
                
                if resFlag == "ns":
                    tldHostname = ip
                    
                    if hostname.lower().endswith("edu"):
                        tldPort = 45002
                    elif hostname.lower().endswith("com"):
                        tldPort = 45001
                    else:
                        tldPort = port

                    idNum += 1
                    
                    tldReq = f"0 {hostname} {idNum} {flag}\n"
                    
                    try:
                        tldSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        tldSocket.connect((tldHostname, tldPort))
                        tldSocket.send(tldReq.encode('utf-8'))
                        
                        tldResponse = tldSocket.recv(1024).decode('utf-8').strip()
                        tldSocket.close()
                        
                        output.write(f"{tldResponse}\n")
                        output.flush()
                        
                    except socket.error as e:
                        print(f"Error connecting to TLD server {tldHostname} on port {tldPort}: {e}")
                
            except socket.error as e:
                print(f"Error connecting to root server {rsHostName}: {e}")

            idNum += 1    
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
