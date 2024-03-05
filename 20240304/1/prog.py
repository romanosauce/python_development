import cowsay
import shlex


class Field:
    size = 10

    def __init__(self):
        self.field = [[0 for i in range(self.size)] for j in range(self.size)]
        self.monsters_pos = {}

    def add_monster(self, x, y, monster):
        if monster.get_name() in cowsay.list_cows():
            subst = False
            if (x, y) in self.monsters_pos:
                subst = True
            self.monsters_pos[(x, y)] = monster
            print(f"Added monster {monster.get_name()} to ({x}, {y}) saying {monster.get_phrase()}")
            if subst:
                print("Replaced the old monster")
        else:
            print("Cannot add unknown monster")

    def get_monster(self, pos):
        return self.monsters_pos[pos]

    def get_monsters_pos(self):
        return self.monsters_pos.keys()

    def encounter(self, x, y):
        pos = (x, y)
        if pos in self.get_monsters_pos():
            print(cowsay.cowsay(self.get_monster(pos).get_phrase(),
                                cow=self.get_monster(pos).get_name()))


class Player:
    _dir_dict = {"up": (0, -1), "down": (0, 1),
                 "left": (-1, 0), "right": (1, 0)}

    def __init__(self, field):
        self.x = 0
        self.y = 0
        self.field = field

    def make_move(self, side):
        dirs = self._dir_dict[side]
        self.x += dirs[0]
        self.y += dirs[1]
        self.x %= Field.size
        self.y %= Field.size
        print(f"Moved to ({self.x}, {self.y})")
        self.field.encounter(self.x, self.y)


class Monster:
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.phrase = kwargs['phrase']
        self.hp = kwargs['hp']

    def get_phrase(self):
        return self.phrase

    def get_name(self):
        return self.name


# Parsing: iterate through parameters and checking
field = Field()
player = Player(field)
while (comm := input()):
    pars_comm = shlex.split(comm)
    err_flag = False
    match pars_comm:
        case [("up" | "down" | "left" | "right") as side, *options]:
            if len(options) != 0:
                print("Invalid arguments")
            else:
                player.make_move(side)
        case ["addmon", *options]:
            if len(options) != 8:
                print("Invalid arguments")
                continue
            param_dict = {}
            param_dict['name'] = options[0]
            opt_set = set()
            i = 1
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
                        i += 3
                    case _:
                        print('Invalid arguments')
                        err_flag = True
                        continue
            if err_flag:
                continue
            if opt_set != {'hello', 'hp', 'coords'}:
                print(6)
                print('Invalid arguments')
                continue
            field.add_monster(x, y, Monster(**param_dict))
        case _:
            print("Invalid command")
