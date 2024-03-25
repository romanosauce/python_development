import sys
import socket
from http.server import test, SimpleHTTPRequestHandler

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", int(sys.argv[1])))
print(s.getsockname()[0])
s.close()

test(HandlerClass=SimpleHTTPRequestHandler, port=int(sys.argv[1]))
