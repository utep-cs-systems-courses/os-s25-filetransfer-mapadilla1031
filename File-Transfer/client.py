#!/usr/bin/env python3
#marko padilla OS 4375 Version 1.3 updated
# client version 1.2
import socket
import sys
import re
import os
from mytar import c_archive

if len(sys.argv) < 3:
    sys.exit(1)
server = sys.argv[1]
files = sys.argv[2:]
try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Cannot parse server '%s'" % server)
    sys.exit(1)

# Socket creation and connection 
s = None
for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        print("creating th sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        print(" error: %s" % msg)
        s = None
        continue
    try:
        print(" try to connect to %s" % repr(sa))
        s.connect(sa)
    except socket.error as msg:
        print(" error: %s" % msg)
        s.close()
        s = None
        continue
    break

if s is None:
    print('could not the open socket .. exit')
    sys.exit(1)

# pipe for data transfering 
r, w = os.pipe()
pid = os.fork()

if pid == 0:  # Child process for the archiver
    os.close(r)
    os.dup2(w, 1)  # Redirect stdout to the pipe
    c_archive(files)
    os.close(w)
    sys.exit(0)
else:  # Parent reads archive and sends to the server
    os.close(w)
    
    # Send data to server in chunks using the fd operations 
    buffer_size = 4000
    
    while True:
        # need to read from the pipe in chunks/parts
        chunk = os.read(r, buffer_size)
        if not chunk:
            break
            
        # Send the parts to the server using os.write on socket fd
        remaining = chunk
        while len(remaining):
            print("sending %d bytes" % len(remaining))
            bytesSent = os.write(s.fileno(), remaining)
            remaining = remaining[bytesSent:]
    
    os.close(r)
    os.waitpid(pid, 0)  # Wait for child process to end here
    s.shutdown(socket.SHUT_WR)
    
    # Receive the response using s.recv() 
    while 1:
        data = s.recv(1024).decode()
        if len(data) == 0:
            break
        print("Received -> '%s'" % data)
    
    print("Zero length read close")
    s.close()

