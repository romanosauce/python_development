import sys
import http.server
import socket

ip = socket.gethostbyname(socket.gethostname())
port = int(sys.argv[1])


