"""Methods for client work."""

import socket
import readline
import shlex
import cmd
import time
import threading
import webbrowser
import pathlib
from ..common import (get_weapons,
                      FIELD_SIZE,
                      READ_FROM_FILE_TIMEOUT)


prompt = ">>> "
doc_path = "docs/build/html/index.html"


class MUD_shell(cmd.Cmd):
    """Class which inherits :class:`cmd.Cmd` to parse and process commands from the user."""

    def __init__(self, socket, timeout=0, *args, **kwargs):
        """Init MUD_shell object."""
        self.socket = socket
        self.timeout = timeout
        self.prompt = ""
        super().__init__(*args, **kwargs)

    def precmd(self, line):
        """Sleep if read from file not to overflood server."""
        time.sleep(self.timeout)
        return super().precmd(line)

    def do_up(self, arg):
        """Process 'up' command."""
        self.socket.sendall("move 0 -1\n".encode())

    def do_down(self, arg):
        """Process 'down' command."""
        self.socket.sendall("move 0 1\n".encode())

    def do_left(self, arg):
        """Process 'left' command."""
        self.socket.sendall("move -1 0\n".encode())

    def do_right(self, arg):
        """Process 'right' command."""
        self.socket.sendall("move 1 0 \n".encode())

    def do_addmon(self, arg):
        """
        Process 'addmon' command.

        And check correctness of given arguments
        """
        options = shlex.split(arg)
        if len(options) != 8:
            print(f"Invalid arguments amount\n{prompt}", end='')
            return
        param_dict = {}
        param_dict['name'] = options[0]
        opt_set = set()
        i = 1
        err_flag = False
        while i < len(options):                                             # TODO: can parameters occure twice?
            match options[i]:
                case 'hello':
                    param_dict['phrase'] = shlex.quote(options[i+1])
                    opt_set.add('hello')
                    i += 2
                case 'hp':
                    try:
                        hp = int(options[i+1])
                    except Exception:
                        print(f"Invalid hp\n{prompt}", end='')
                        err_flag = True
                        break
                    if not (hp > 0):
                        print(f"Invalid hp\n{prompt}", end='')
                        err_flag = True
                        break
                    param_dict['hp'] = hp
                    opt_set.add('hp')
                    i += 2
                case 'coords':
                    try:
                        x = int(options[i+1])
                        y = int(options[i+2])
                    except Exception:
                        print(f"Invalid coords\n{prompt}", end='')
                        err_flag = True
                        break
                    if not (0 <= x <= FIELD_SIZE and 0 <= y <= FIELD_SIZE):
                        print(f"Invalid coords\n{prompt}", end='')
                        err_flag = True
                        break
                    opt_set.add('coords')
                    param_dict['coords_x'] = x
                    param_dict['coords_y'] = y
                    i += 3
                case _:
                    print(f"Invalid arguments\n{prompt}", end='')
                    err_flag = True
                    return
        if err_flag:
            return
        if opt_set != {'hello', 'hp', 'coords'}:
            print(f"Missing required arguments\n{prompt}", end='')
            return
        opts = 'addmon'
        for opt in 'name', 'coords_x', 'coords_y', 'phrase', 'hp':
            opts += ' ' + str(param_dict[opt])
        self.socket.sendall((opts+'\n').encode())

    def do_attack(self, arg):
        """Process 'attack' command."""
        arg = shlex.split(arg)
        if len(arg) == 1:
            weapon = "sword"
        elif len(arg) == 3:
            match arg[1:]:
                case ['with', arms]:
                    if arms not in get_weapons():
                        print(f"Unknown weapon\n{prompt}", end='')
                        return
                    else:
                        weapon = arms
                case _:
                    print(f"Unknown arguments\n{prompt}", end='')
                    return
        else:
            print(f"Unknown arguments\n{prompt}", end='')
            return
        self.socket.sendall(f"attack {arg[0]} {weapon}\n".encode())

    def do_sayall(self, arg):
        """Process 'sayall' command."""
        self.socket.sendall(f"sayall {arg}\n".encode())

    def do_movemonsters(self, arg):
        """Process 'movemonsters' command."""
        match arg:
            case 'on':
                msg = "movemonsters on"
                self.socket.sendall((msg + '\n').encode())
            case 'off':
                msg = "movemonsters off"
                self.socket.sendall((msg + '\n').encode())
            case _:
                print(f"Invalid arguments\n{prompt}", end='')

    def do_locale(self, arg):
        """Process 'locale' command."""
        self.socket.sendall(f"locale {arg}\n".encode())
        print(prompt, end="")

    def do_documentation(self, arg):
        """Open generated documentation."""
        webbrowser.open(str(pathlib.Path(doc_path).absolute()))

    def do_EOF(self, arg):
        """If EOF is seen, return 1."""
        return 1

    def emptyline(self):
        """If emptyline do nothing."""
        pass


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


def start_client(login, in_file=None):
    host = "localhost"
    port = 1337

    from_file = True if in_file else False

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        msg_handler = threading.Thread(target=msg_reciever,
                                       args=(s, prompt))
        msg_handler.start()
        s.sendall((login + '\n').encode())
        if from_file:
            with open(in_file, 'r') as f:
                shell = MUD_shell(s, timeout=READ_FROM_FILE_TIMEOUT, stdin=f)
                shell.use_rawinput = False
                shell.cmdloop()
        else:
            shell = MUD_shell(s)
        shell.cmdloop()
