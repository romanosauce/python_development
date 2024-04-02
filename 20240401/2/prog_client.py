import sys
import threading
import socket
import readline


# https://stackoverflow.com/questions/48024720/python-how-to-check-if-socket-is-still-connected
def is_socket_closed(sock: socket.socket) -> bool:
    try:
        # this will try to read bytes without blocking and also without removing them from buffer (peek only)
        data = sock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
        if len(data) == 0:
            return True
    except BlockingIOError:
        return False  # socket is open and reading from it would block
    except ConnectionResetError:
        return True  # socket was closed for some other reason
    except Exception as e:
        return False
    return False


def msg_reciever(socket):
    while True:
        if is_socket_closed(socket):
            print("Server is down")
            quit(1)
            break
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
