import cowsay
import io
import shlex
import sys
import cmd


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
            print(f"Added monster {monster.get_name()} to ({x}, {y}) saying {monster.get_phrase()}")
            if subst:
                print("Replaced the old monster")
        else:
            print("Cannot add unknown monster")

    def delete_mon(self, coords):
        self.monsters_pos.pop(coords)

    def get_monster(self, pos):
        return self.monsters_pos[pos]

    def get_monsters_pos(self):
        return self.monsters_pos.keys()

    def encounter(self, x, y):
        pos = (x, y)
        if pos in self.get_monsters_pos():
            monster = self.get_monster(pos)
            if monster.get_custom():
                print(cowsay.cowsay(monster.get_phrase(),
                                    cowfile=cows_dict[monster.get_name()]))
            else:
                print(cowsay.cowsay(monster.get_phrase(),
                                    cow=monster.get_name()))


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
        print(f"Moved to ({self.x}, {self.y})")
        self.field.encounter(self.x, self.y)

    def attack(self, name, weapon):
        damage = self.weapons[weapon]
        pos = (self.x, self.y)
        if (pos in self.field.get_monsters_pos() and
                self.field.get_monster(pos).get_name() == name):
            monster = self.field.get_monster(pos)
            damage = damage if monster.get_hp() > damage else monster.get_hp()
            print(f"Attacked {monster.get_name()}"
                  f", damage {damage} hp")
            monster.get_damage(damage)
        else:
            print(f"No {name} here")


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
        if damage < self.hp:
            self.hp -= damage
            print(f"{self.name} now has {self.hp}")
        else:
            print(f"{self.name} died")
            field.delete_mon(self.coords)


class MUD_shell(cmd.Cmd):
    prompt = "python-MUD>> "

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
        if len(options) != 8:
            print("Invalid arguments")
            return
        param_dict = {}
        param_dict['name'] = options[0]
        opt_set = set()
        i = 1
        err_flag = False
        while i < len(options):                                             # TODO: can parameters occure twice?
            match options[i]:
                case 'hello':
                    param_dict['phrase'] = options[i+1]
                    opt_set.add('hello')
                    i += 2
                case 'hp':
                    try:
                        hp = int(options[i+1])
                    except Exception:
                        print('Invalid arguments')
                        err_flag = True
                        break
                    if not (hp > 0):
                        print('Invalid arguments')
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
                        print('Invalid arguments')
                        err_flag = True
                        break
                    if not (0 <= x <= Field.size and 0 <= y <= Field.size):
                        print('Invalid arguments')
                        err_flag = True
                        break
                    opt_set.add('coords')
                    param_dict['coords'] = (x, y)
                    i += 3
                case _:
                    print('Invalid arguments')
                    err_flag = True
                    return
        if err_flag:
            return
        if opt_set != {'hello', 'hp', 'coords'}:
            print(6)
            print('Invalid arguments')
            return
        field.add_monster(x, y, Monster(**param_dict))

    def do_attack(self, arg):
        arg = shlex.split(arg)
        weapon = 'sword'
        if len(arg) == 1:
            player.attack(arg[0], weapon)
        elif len(arg) == 3:
            match arg[1:]:
                case ['with', arms]:
                    if arms not in player.get_weapons():
                        print("Unknown weapon")
                    else:
                        player.attack(arg[0], arms)
                case _:
                    print("Invalid arguments")
                    return
        else:
            print("Invalid arguments")
            return

    def do_EOF(self, arg):
        return 1

    def complete_attack(self, text, line, begidx, endidx):
        args = (line[:endidx] + '.').split()
        if len(args) == 2:
            return [c for c in (set(cowsay.list_cows()) | set(cows_dict.keys())) if
                    c.startswith(text)]
        if len(args) == 4:
            return [arm for arm in player.get_weapons() if arm.startswith(text)]


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

print("<<< Welcome to Python-MUD 0.1 >>>")
# Parsing: iterate through parameters and checking
field = Field()
player = Player(field)
source_file = sys.stdin

if source_file == sys.stdin:
    MUD_shell().cmdloop()
