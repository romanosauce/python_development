import socket
import sys
import shlex

host = "localhost" if len(sys.argv) < 2 else sys.argv[1]
port = 1337 if len(sys.argv) < 3 else int(sys.argv[2])
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while data := conn.recv(1024):
            args = shlex.split(data.decode())
            match args:
                case ['print', *other]:
                    conn.sendall(shlex.join(other).encode())
                case ['info', 'host']:
                    conn.sendall(str(addr[0]).encode())
                case ['info', 'port']:
                    conn.sendall(str(addr[1]).encode())
