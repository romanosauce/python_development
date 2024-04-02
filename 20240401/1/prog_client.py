import sys
import threading
import socket
import readline


def msg_reciever(socket):
    while True:
        msg = socket.recv(1024).decode()
        buf = readline.get_line_buffer()
        if buf:
            print(f"\n{msg}\n{prompt}{buf}", end="",
                  flush=True)
        else:
            print('', end='\033[2K\033[1G')
            print(f"{msg}\n{prompt}{buf}", end="",
                  flush=True)


host = "localhost"
port = 1337
if len(sys.argv) == 1:
    print("Please provide your login name")
    quit(1)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    prompt = ">>> "
    s.connect((host, port))
    msg_handler = threading.Thread(target=msg_reciever,
                                   args=(s, ))
    msg_handler.start()
    s.sendall((sys.argv[1]+'\n').encode())
    while True:
        cmd = input()
        s.sendall((cmd+'\n').encode())
