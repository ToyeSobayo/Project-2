import sys
import socket

def loadRsDatabase(filename):
    tldMap = {}
    directMap = {}

    with open(filename, 'r') as f:
        lines = f.readlines()
    
    if len(lines) < 2:
        raise Exception("File must have at least two lines for TLD mapping")
    
    ts1Line = lines[0].strip()
    ts2Line = lines[1].strip()

    ts1Parts = ts1Line.split()
    ts2Parts = ts2Line.split()

    if len(ts1Parts) != 2 or len(ts2Parts) != 2:
        raise Exception("First two lines must contain exactly two values")
    
    # tldMap stores TLD and corresponding TS hostname
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
            print("Error: Unexpected format", line)
    
    return tldMap, directMap

def forwardToTS(ts_hostname, port, query):
    try:
        ts_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ts_sock.connect((ts_hostname, port))
        ts_sock.send(query.encode('utf-8'))
        response = ts_sock.recv(1024).decode('utf-8').strip()
        ts_sock.close()
        return response
    except Exception as e:
        print("Error forwarding query to TS server", ts_hostname, ":", e)
        return None

def processQuery(query, tldMap, directMap, port):
    parts = query.split()
    if len(parts) != 4:
        return None
    qtype, domain, ident, qflag = parts
    domain_lower = domain.lower()
    
    delegated = False
    for key in tldMap:
        tld, ts_hostname = tldMap[key]
        if domain_lower.endswith(tld):
            delegated = True
            if qflag == "it":
                return f"1 {domain} {ts_hostname} {ident} ns"
            elif qflag == "rd":
                ts_response = forwardToTS(ts_hostname, port, query)
                if ts_response:
                    ts_parts = ts_response.split()
                    if len(ts_parts) == 5 and ts_parts[4] == "aa":
                        ts_parts[4] = "ra"
                        ts_response = " ".join(ts_parts)
                    return ts_response
                else:
                    return f"1 {domain} 0.0.0.0 {ident} nx"
            else:
                return f"1 {domain} 0.0.0.0 {ident} nx"
    if domain_lower in directMap:
        ip = directMap[domain_lower]
        return f"1 {domain} {ip} {ident} aa"
    else:
        return f"1 {domain} 0.0.0.0 {ident} nx"

def server():
    try:
        tldMap, directMap = loadRsDatabase("../testcases/rsdatabase.txt")
    except Exception as e:
        print("Error loading RS database:", e)
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
    
    log_file = open("rsresponses.txt", "w")
    
    try:
        while True:
            csockid, addr = ss.accept()
            print("Connection from", addr)
            query = csockid.recv(1024).decode('utf-8').strip()
            print("Received query:", query)
            if not query:
                csockid.close()
                continue
            
            response = processQuery(query, tldMap, directMap, port)
            if response is None:
                parts = query.split()
                if len(parts) >= 3:
                    domain = parts[1]
                    ident = parts[2]
                else:
                    domain = "unknown"
                    ident = "0"
                response = f"1 {domain} 0.0.0.0 {ident} nx"
            response += "\n"
            csockid.send(response.encode('utf-8'))
            log_file.write(response)
            log_file.flush()
            csockid.close()
    except KeyboardInterrupt:
        print("Shutting down RS server.")
    except socket.error as e:
        print("Socket error:", e)
    finally:
        log_file.close()
        ss.close()
        print("Server closed on port", port)

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
