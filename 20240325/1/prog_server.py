import cowsay
import io
import shlex
import sys
import cmd
import socket
from collections import deque

msg_queue = deque()
err_flag = False


class Field:
    size = 10

    def __init__(self):
        self.field = [[0 for i in range(self.size)] for j in range(self.size)]
        self.monsters_pos = {}

    def add_monster(self, x, y, monster):
        if monster.get_name() in cowsay.list_cows() or \
                monster.get_name() in cows_dict:
            if monster.get_name() in cows_dict:
                monster.set_custom(True)
            subst = False
            if (x, y) in self.monsters_pos:
                subst = True
            self.monsters_pos[(x, y)] = monster
            text = f"f\x00{monster.get_name()}\x00{x} {y}\x00{monster.get_phrase()}"
            if subst:
                text += "\x00Replaced the old monster"
            msg_queue.append(text)
        else:
            msg_queue.append("t\x00Cannot add unknown monster")

    def delete_mon(self, coords):
        self.monsters_pos.pop(coords)

    def get_monster(self, pos):
        return self.monsters_pos[pos]

    def get_monsters_pos(self):
        return self.monsters_pos.keys()

    def encounter(self, x, y):
        pos = (x, y)
        if pos in self.get_monsters_pos():
            text = msg_queue.pop()
            monster = self.get_monster(pos)
            if not monster.get_custom():
                text += f"\x00{monster.get_name()}\x00{monster.get_phrase()}"
            else:
                text = "t\x00You encountered a custom monster. You are lucky!"
            msg_queue.append(text)


class Player:
    _dir_dict = {"up": (0, -1), "down": (0, 1),
                 "left": (-1, 0), "right": (1, 0)}

    weapons = {"sword": 10, "spear": 15, "axe": 20}

    def __init__(self, field):
        self.x = 0
        self.y = 0
        self.field = field

    def get_weapons(self):
        return self.weapons

    def make_move(self, side):
        dirs = self._dir_dict[side]
        self.x += dirs[0]
        self.y += dirs[1]
        self.x %= Field.size
        self.y %= Field.size
        msg_queue.append(f"f\x00{self.x} {self.y}")
        self.field.encounter(self.x, self.y)

    def attack(self, name, weapon):
        damage = self.weapons[weapon]
        pos = (self.x, self.y)
        if (pos in self.field.get_monsters_pos() and
                self.field.get_monster(pos).get_name() == name):
            monster = self.field.get_monster(pos)
            damage = damage if monster.get_hp() > damage else monster.get_hp()
            msg_queue.append(f"f\x00{monster.get_name()}\x00"
                  f"{damage}")
            monster.get_damage(damage)
        else:
            msg_queue.append(f"t\x00No {name} here")


class Monster:
    def __init__(self, custom=False, **kwargs):
        self.name = kwargs['name']
        self.phrase = kwargs['phrase']
        self.hp = kwargs['hp']
        self.custom = custom
        self.coords = kwargs['coords']

    def set_custom(self, val):
        self.custom = val

    def get_custom(self):
        return self.custom

    def get_phrase(self):
        return self.phrase

    def get_name(self):
        return self.name

    def get_hp(self):
        return self.hp

    def get_damage(self, damage):
        text = msg_queue.pop()
        self.hp -= damage
        if self.hp == 0:
            field.delete_mon(self.coords)
        text += f"\x00{self.hp}"
        msg_queue.append(text)


class MUD_shell(cmd.Cmd):
    def do_up(self, arg):
        player.make_move("up")

    def do_down(self, arg):
        player.make_move("down")

    def do_right(self, arg):
        player.make_move("right")

    def do_left(self, arg):
        player.make_move("left")

    def do_addmon(self, arg):
        options = shlex.split(arg)
        param_dict = {}
        param_dict['name'] = options[0]
        param_dict['coords'] = (int(options[1]), int(options[2]))
        param_dict['phrase'] = options[3]
        param_dict['hp'] = int(options[4])
        field.add_monster(int(options[1]), int(options[2]), Monster(**param_dict))

    def do_attack(self, arg):
        options = shlex.split(arg)
        player.attack(options[0], options[1])


jgsbat = cowsay.read_dot_cow(io.StringIO('''
$the_cow = <<EOC;
         $thoughts
          $thoughts
    ,_                    _,
    ) '-._  ,_    _,  _.-' (
    )  _.-'.|\\\\--//|.'-._  (
     )'   .'\/o\/o\/'.   `(
      ) .' . \====/ . '. (
       )  / <<    >> \  (
        '-._/``  ``\_.-'
  jgs     __\\\\'--'//__
         (((""`  `"")))EOC
'''))

cows_dict = {'jgsbat': jgsbat}

# Parsing: iterate through parameters and checking
field = Field()
player = Player(field)
source_file = sys.stdin

shell = MUD_shell()
# if source_file == sys.stdin:
    # shell.cmdloop()
HOST = 'localhost'
PORT = 1337
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            shell.onecmd(data)
            conn.sendall(msg_queue.popleft().encode())
