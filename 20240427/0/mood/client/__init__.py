"""Functions for receive messages in parallel."""

import socket
import readline


# https://stackoverflow.com/questions/48024720/python-how-to-check-if-socket-is-still-connected
def is_socket_closed(sock: socket.socket) -> bool:
    """
    Determine whether the socket is closed.

    :param sock: socket to check it's availability
    :type sock: :class:`socket.socket`
    """
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


def msg_reciever(socket, prompt):
    """
    Receive message and output it.

    If user starts writing input but didn't press enter,
    output this input after a message

    :param socket: socket to listen on
    :param prompt: print this prompt after the message
    :type socket: :class:`socket.socket`
    :type prompt: str
    """
    while True:
        if is_socket_closed(socket):
            print("Server is down")
            quit(1)
            break
        try:
            msg = socket.recv(1024).decode()
        except Exception as e:
            print("Socket is now closed\nExiting...")
            quit()
        buf = readline.get_line_buffer()
        if buf:
            print(f"\n{msg}\n{prompt}{buf}", end="",
                  flush=True)
        else:
            print('', end='\033[2K\033[1G')
            print(f"{msg}\n{prompt}{buf}", end="",
                  flush=True)
