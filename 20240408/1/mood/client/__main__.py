"""Module for starting client and print received data in parallel."""

from . import prog_client
import sys
import socket
import threading


host = "localhost"
port = 1337
if len(sys.argv) == 1:
    print("Please provide your login name")
    quit(1)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    prompt = ">>> "
    s.connect((host, port))
    msg_handler = threading.Thread(target=prog_client.msg_reciever,
                                   args=(s, prompt))
    msg_handler.start()
    s.sendall((sys.argv[1]+'\n').encode())
    while True:
        cmd = input()
        s.sendall((cmd+'\n').encode())
