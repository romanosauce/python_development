import socket
import sys
import shlex
import cowsay

field_size = 10


def parse_command(line):
    opt = shlex.split(msg.decode())
    match opt:
        case [("up" | "down" | "left" | "right") as side, *options]:
            if len(options) != 0:
                raise Exception("Invalid arguments")
            else:
                return (side, [])
        case ["addmon", *options]:
            if len(options) != 8:
                raise Exception("Invalid arguments")
            param_dict = {}
            param_dict['name'] = options[0]
            opt_set = set()
            i = 1
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
                            raise Exception('Invalid arguments')
                        if not (hp > 0):
                            raise Exception('Invalid arguments')
                        param_dict['hp'] = hp
                        opt_set.add('hp')
                        i += 2
                    case 'coords':
                        try:
                            x = int(options[i+1])
                            y = int(options[i+2])
                        except Exception:
                            raise Exception('Invalid arguments')
                        if not (0 <= x <= field_size and 0 <= y <= field_size):
                            raise Exception('Invalid arguments')
                        opt_set.add('coords')
                        param_dict['coords_x'] = x
                        param_dict['coords_y'] = y
                        i += 3
                    case _:
                        raise Exception('Invalid arguments')
            if opt_set != {'hello', 'hp', 'coords'}:
                raise Exception('Invalid arguments')
            opts = []
            for opt in 'name', 'coords_x', 'coords_y', 'phrase', 'hp':
                opts.append(str(param_dict[opt]))
            return ("addmon", opts)
        case ['attack', *options]:
            if len(options) == 1:
                return ('attack', [options[0], 'sword'])
            elif len(options) == 3:
                match options[1:]:
                    case ['with', arms]:
                        return ('attack', [options[0], arms])
                    case _:
                        raise Exception("Invalid arguments")
            else:
                raise Exception("Invalid arguments")
        case _:
            raise Exception("Unknown command")


host = "localhost" if len(sys.argv) < 2 else sys.argv[1]
port = 1337 if len(sys.argv) < 3 else int(sys.argv[2])
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))
    while msg := sys.stdin.buffer.readline():
        try:
            command, options = parse_command(msg.decode())
        except Exception as ex:
            print(ex)
            continue
        s.sendall(b' '.join([command.encode()] + list(map(str.encode, options))))
        rcv_data = s.recv(1024).rstrip()
        error, *options = map(bytes.decode, rcv_data.split(b'\x00'))
        if error == 't':
            print(options[0])
            continue
        match command:
            case "up" | "down" | "left" | "right":
                x, y = options[0].split()
                print(f"Moved to ({x}, {y})")
                if len(options) == 3:
                    monster = options[1]
                    saying = options[2]
                    print(cowsay.cowsay(saying, cow=monster))
            case 'attack':
                monster, damage, hp = options[0], options[1], options[2]
                print(f"Attacked {monster}, damage {damage} hp")
                if options[2] == '0':
                    print(f"{monster} died")
                else:
                    print(f"{monster} now has {hp}")
            case 'addmon':
                x, y = options[1].split()
                name = options[0]
                phrase = options[2]
                print(f"Added monster {name} to ({x}, {y}) saying {phrase}")
                if len(options) == 4:
                    print(options[3])
            case _:
                print("Error with server response")
