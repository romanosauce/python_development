"""Module for starting client and print received data in parallel."""

from . import msg_reciever
import sys
import socket
import threading
import time


READ_FROM_FILE_TIMEOUT = 3


host = "localhost"
port = 1337
if len(sys.argv) == 1:
    print("Please provide your login name")
    quit(1)
login_name = sys.argv[1]

from_file = False
if '--file' in sys.argv[2:]:
    i = sys.argv.index('--file', 2)
    try:
        file_name = sys.argv[i+1]
    except Exception as e:
        print('Please provide a file name')
        quit(1)
    from_file = True

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    prompt = ">>> "
    s.connect((host, port))
    msg_handler = threading.Thread(target=msg_reciever,
                                   args=(s, prompt))
    msg_handler.start()
    s.sendall((sys.argv[1]+'\n').encode())
    if from_file:
        with open(file_name, 'r') as f:
            for cmd in f:
                s.sendall(cmd.encode())
                time.sleep(READ_FROM_FILE_TIMEOUT)

    else:
        while True:
            cmd = input()
            s.sendall((cmd+'\n').encode())
