import cowsay


class Field:
    size = 10

    def __init__(self):
        self.field = [[0 for i in range(self.size)] for j in range(self.size)]
        self.monsters_pos = {}

    def add_monster(self, x, y, monster):
        subst = False
        if (x, y) in self.monsters_pos:
            subst = True
        self.monsters_pos[(x, y)] = monster
        print(f"Added monster to ({x}, {y}) saying {monster.get_phrase()}")
        if subst:
            print("Replaced the old monster")

    def get_monster(self, pos):
        return self.monsters_pos[pos]

    def get_monsters_pos(self):
        return self.monsters_pos.keys()

    def encounter(self, x, y):
        pos = (x, y)
        if pos in self.get_monsters_pos():
            print(cowsay.cowsay(self.get_monster(pos).get_phrase()))


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
    def __init__(self, phrase):
        self.phrase = phrase

    def get_phrase(self):
        return self.phrase


field = Field()
player = Player(field)
while (comm := input()):
    pars_comm = comm.split()
    match pars_comm:
        case [("up" | "down" | "left" | "right") as side, *options]:
            if len(options) != 0:
                print("Invalid arguments")
            else:
                player.make_move(side)
        case ["addmon", *options]:
            if len(options) != 3:
                print("Invalid arguments")
            else:
                try:
                    x = int(options[0])
                    y = int(options[1])
                except Exception:
                    print("Invalid arguments")
                    continue
                if not (0 <= x <= 9 and 0 <= y <= 9):
                    print("Invalid arguments")
                else:
                    phrase = options[2]
                    field.add_monster(int(x), int(y), Monster(phrase))
        case _:
            print("Invalid command")
