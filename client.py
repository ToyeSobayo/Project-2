import sys
import socket

def client():
    # Host names to resolve from input file
    try:
        with open('../testcases/hostnames.txt', 'r') as file:
            hostnames = file.read().strip().split('\n')
    except FileNotFoundError:
        print("Error: hostnames.txt not found")
        sys.exit(1)
    
    # Open output file
    with open('../testcases/resolved.txt', 'w') as output_file:
        # Counter for identification field
        identification = 1
        
        for line in hostnames:
            parts = line.strip().split()
            if len(parts) != 2:
                print(f"Invalid format in hostnames.txt: {line}")
                continue
            hostname, flag = parts
            
            # Create RU-DNS request
            request = f"0 {hostname} {identification} {flag}\n"
            
            # Connect to root server first
            try:
                rs_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                rs_socket.connect((rsHostName, port))
                rs_socket.send(request.encode('utf-8'))
                
                # Receive response from root server
                response = rs_socket.recv(1024).decode('utf-8').strip()
                rs_socket.close()
                
                # Parse response
                response_parts = response.split()
                if len(response_parts) != 5:
                    print(f"Invalid response format: {response}")
                    continue
                    
                resp_type, domain, ip, resp_id, resp_flag = response_parts
                
                # Write response to output file
                output_file.write(f"{response}\n")
                output_file.flush()
                
                # Check if we need to contact a TLD server (iterative query)
                if resp_flag == "ns":
                    # Get TLD server hostname from the response (for local testing, likely "localhost")
                    tld_hostname = ip
                    
                    # Determine the appropriate port based on the queried domain's TLD
                    # For local testing: TS1 on port 45001 for .com, TS2 on port 45002 for .edu
                    if hostname.lower().endswith("edu"):
                        tld_port = 45002
                    elif hostname.lower().endswith("com"):
                        tld_port = 45001
                    else:
                        tld_port = port  # fallback if unknown TLD
                        
                    # Increment identification for new query
                    identification += 1
                    
                    # Create new request for TLD server
                    tld_request = f"0 {hostname} {identification} {flag}\n"
                    
                    # Connect to TLD server
                    try:
                        tld_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        tld_socket.connect((tld_hostname, tld_port))
                        tld_socket.send(tld_request.encode('utf-8'))
                        
                        # Receive response from TLD server
                        tld_response = tld_socket.recv(1024).decode('utf-8').strip()
                        tld_socket.close()
                        
                        # Write TLD response to output file
                        output_file.write(f"{tld_response}\n")
                        output_file.flush()
                        
                    except socket.error as e:
                        print(f"Error connecting to TLD server {tld_hostname} on port {tld_port}: {e}")
                
            except socket.error as e:
                print(f"Error connecting to root server {rsHostName}: {e}")

            # Increment identification for next query
            identification += 1    
            # by this time it should be able to resolve the hostname to the IP address
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
