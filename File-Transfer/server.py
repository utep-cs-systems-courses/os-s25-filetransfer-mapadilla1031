#!/usr/bin/env python3
#server version 1.2
import socket
import sys
import os
from mytar import x_archive

# Parse command line arguments
if len(sys.argv) < 2:
    sys.exit(1)

listenPort = int(sys.argv[1])
listenAddr = ''  #for all available interfaces

# Create server socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((listenAddr, listenPort))
s.listen(3)  

while True:#accepts multiple concurrent clients, and gives new socket cnn 
    conn, addr = s.accept()  # waiting until the incoming connection request then (and accept it)
    print('Connected', addr)
    
    # Fork for client
    pid = os.fork()
    
    if pid == 0:  # Child p
        s.close()
        # get the data the from client
        received_data = b''
        while True:
            data = conn.recv(1000)
            if len(data) == 0:
                break#just break if nothing recieved
            received_data += data
        
        # Process the archive
        # Create pipe for extraction
        r, w = os.pipe()
        extract_pid = os.fork()
        
        if extract_pid == 0:  # Child process for extraction
            os.close(w)
            os.dup2(r, 0)  # Redirect read end to stdin
            os.close(r)
            x_archive()  # Extract files from the archiver
            sys.exit(0)
        else:  # P process
            os.close(r)
            os.write(w, received_data)  #data to pipe
            os.close(w)
            os.waitpid(extract_pid, 0)  # Waiting for the extraction to end
        
        # Send response to client
        messageToClient = "Files have been received !".encode()
        while len(messageToClient):
            bytesSent = conn.send(messageToClient)
            messageToClient = messageToClient[bytesSent:]
        
        conn.shutdown(socket.SHUT_WR)
        conn.close()
        sys.exit(0)  # Child process is done and end connection 
    
    else:  # Parent process
        conn.close()