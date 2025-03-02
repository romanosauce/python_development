"""Main logic for managing connections and handling user commands."""
import cowsay
import io
import shlex
import cmd
import asyncio
import random


TIME_INTERVAL_FOR_MOVING_MONSTER = 30


class Field:
    """
    A main class with implementation of game logic.

    It is used to represent dungeon field with players and monsters.
    Stores monsters' positions, adds and deletets monster to a field
    """

    size: int = 10
    """Width (in cells) of the field."""

    def __init__(self):
        self.field = [[0 for i in range(self.size)] for j in range(self.size)]
        self.monsters_pos = {}

    def add_monster(self, x, y, monster, id):
        """
        Add monster to a field.

        :param x: x coordinate
        :type x: int
        :param y: y coordinate
        :type y: int
        :param monster: Monster object representing a monster
        :type monster: :class:`Monster`
        """
        if monster.get_name() in cowsay.list_cows() or \
                monster.get_name() in cows_dict:
            if monster.get_name() in cows_dict:
                monster.set_custom(True)
            subst = False
            if (x, y) in self.monsters_pos:
                subst = True
            self.monsters_pos[(x, y)] = monster
            msg = f"{clients[id].get_name()} added monster {monster.get_name()} to ({x}, {y}) saying {monster.get_phrase()}"
            broadcast_queue[id].put_nowait(msg)
            if subst:
                broadcast_queue[id].put_nowait("Replaced the old monster")
        else:
            clients_queue[id].put_nowait("Cannot add unknown monster")

    def delete_mon(self, coords):
        """
        Delete monster from a field.

        :param coords: coordinates of monster to delete
        :type coords: tuple(int, int)
        """
        self.monsters_pos.pop(coords)

    def get_monster(self, pos):
        """
        Get monster from a field.

        :param pos: coords where monster should be added
        :type pos: tuple(int, int)
        :return: instance of :class:`Monster` from cell
        """
        return self.monsters_pos[pos]

    def get_monsters_pos(self):
        """:return: `key_dict` with positions of all monsters."""
        return self.monsters_pos.keys()

    def encounter(self, x, y, id):
        """
        If player move to a cell with monster, send player a notification.

        :param x: x coordinate of player
        :param y: y coordinate of player
        :param id: identifier of client who meets monster
        :type x: int
        :type y: int
        :type id: str
        """
        pos = (x, y)
        if pos in self.get_monsters_pos():
            monster = self.get_monster(pos)
            if monster.get_custom():
                msg = cowsay.cowsay(monster.get_phrase(),
                                    cowfile=cows_dict[monster.get_name()])
            else:
                msg = cowsay.cowsay(monster.get_phrase(),
                                    cow=monster.get_name())
            clients_queue[id].put_nowait(msg)

    def wandering_monster(self):
        """
        Move random monster per TIME_INTERVAL_FOR_MOVING_MONSTER secоnds interval.

        If monster ended up in a cell with clients, send them a notification
        """
        monsters_pos = list(self.get_monsters_pos())
        if monsters_pos:
            chosed_monster_coords = random.choice(monsters_pos)
            chosed_monster_x, chosed_monster_y = chosed_monster_coords
            side, chosed_dir = random.choice(list(Player._dir_dict.items()))
            chosed_dir_x, chosed_dir_y = chosed_dir
            new_mon_coords = ((chosed_monster_x+chosed_dir_x) % self.size,
                              (chosed_monster_y+chosed_dir_y) % self.size)
            while new_mon_coords in monsters_pos:
                chosed_monster_coords = random.choice(monsters_pos)
                chosed_monster_x, chosed_monster_y = chosed_monster_coords
                side, chosed_dir = random.choice(list(Player._dir_dict.items()))
                chosed_dir_x, chosed_dir_y = chosed_dir
                new_mon_coords = ((chosed_monster_x+chosed_dir_x) % self.size,
                                  (chosed_monster_y+chosed_dir_y) % self.size)
            monster = self.get_monster(chosed_monster_coords)
            self.delete_mon(chosed_monster_coords)
            self.monsters_pos[new_mon_coords] = monster
            msg = f"{monster.get_name()} moved to {new_mon_coords}"
            # msg = f"{monster.get_name()} moved one cell {side}"
            for client_id in clients:
                clients_queue[client_id].put_nowait(msg)
                self.encounter(*clients[client_id].get_coords(), client_id)


class Player:
    """
    Class representing a player who interacts with field, monsters and other users

    :param field: :class:`Field` object where to place the player
    :type field: :class:`Field`
    :param id: identifier of client associated with player
    :type id: str
    :param name: client's login
    :type name: str
    """

    _dir_dict = {"up": (0, -1), "down": (0, 1),
                 "left": (-1, 0), "right": (1, 0)}
    """Mapping direction name to changes of coordinates."""

    weapons = {"sword": 10, "spear": 15, "axe": 20}
    """Available weapons for user's attack."""

    def __init__(self, field, id, name):
        self.x = 0
        self.y = 0
        self.field = field
        self.id = id
        self.name = name

    def get_weapons(self):
        """:return: available weapons."""
        return self.weapons

    def get_name(self):
        """:return: client's login."""
        return self.name

    def get_id(self):
        """:return: client's id."""
        return self.id

    def get_coords(self):
        """:return: player's current coordinates."""
        return (self.x, self.y)

    def make_move(self, side):
        """
        Move player on the field in some direction.

        :param side: name of the side (up, down, left, right)
        :type side: str
        """
        dirs = self._dir_dict[side]
        self.x += dirs[0]
        self.y += dirs[1]
        self.x %= Field.size
        self.y %= Field.size
        clients_queue[self.id].put_nowait(f"Moved to ({self.x}, {self.y})")
        self.field.encounter(self.x, self.y, self.id)

    def attack(self, name, weapon):
        """
        Perform attack on monster.

        If no monster is in the cell where the player is, send notification

        :param name: name of the monster being attacked
        :type name: str
        :param weapon: weapon used for an attack
        :type weapon: str
        """
        damage = self.weapons[weapon]
        pos = (self.x, self.y)
        if (pos in self.field.get_monsters_pos() and
                self.field.get_monster(pos).get_name() == name):
            monster = self.field.get_monster(pos)
            damage = damage if monster.get_hp() > damage else monster.get_hp()
            msg = f"{self.name} attacked {monster.get_name()} with {weapon}\ncausing {damage} hp damage"
            broadcast_queue[self.id].put_nowait(msg)
            monster.get_damage(damage, self.id)
        else:
            clients_queue[self.id].put_nowait(f"No {name} here")

    def sayall(self, msg):
        """
        Send message to all users on the field.

        :param msg: message to send
        :type msg: str
        """
        msg = f"{self.name}: {msg}"
        broadcast_queue[self.id].put_nowait(msg)


class Monster:
    """
    Class representing monster on the field.

    :param custom: specify if monster is custom, that is defined in other place
    :type custom: boolean
    :param kwargs: dict with info about monster

                - 'name' : monster name, must be correct name of default monsters or name of custom defined monster

                - 'pharse' : message which is being send to client while he meets monster in the field

                - 'coords' : coordinates where the monster should be placed

                - 'hp' : health points of the monster
    """

    def __init__(self, custom=False, **kwargs):
        """
        Initialize empty Monster object.

        Parameters:
            custom : boolean
                specify if monster is custom, that is defined in other place
            kwargs : dict with info about monster
                'name' : monster name, must be correct name of default monsters
                    or name of custom defined monster
                'pharse' : message which is being send to client while he
                    meets monster in the field
                'coords' : coordinates where the monster should be placed
                'hp' : health points of the monster
        """
        self.name = kwargs['name']
        self.phrase = kwargs['phrase']
        self.hp = kwargs['hp']
        self.custom = custom
        self.coords = kwargs['coords']

    def set_custom(self, val):
        """Set if this monster is custom monster."""
        self.custom = val

    def get_custom(self):
        """:return: custom flag of the monster."""
        return self.custom

    def get_phrase(self):
        """:return: monster's phrase."""
        return self.phrase

    def get_name(self):
        """:return: monster's name."""
        return self.name

    def get_hp(self):
        """:return: monster's hp."""
        return self.hp

    def get_damage(self, damage, id):
        """
        Make monster get damage from the player.

        If after attack monster has 0 hp, deletes monster from the field
        """
        if damage < self.hp:
            self.hp -= damage
            broadcast_queue[id].put_nowait(f"{self.name} now has {self.hp}")
        else:
            broadcast_queue[id].put_nowait(f"{self.name} died")
            field.delete_mon(self.coords)


class MUD_shell(cmd.Cmd):
    """
    Class which inherits :class:`cmd.Cmd` to parse and process commands from the user.

    :param player: :class:`Player` object with whom this class instance is associated
    :type player: :class:`Player`
    """

    def __init__(self, player: Player):
        self.player = player
        self.id = player.get_id()

    def do_up(self, arg):
        """Process 'up' command."""
        self.player.make_move("up")

    def do_down(self, arg):
        """Process 'down' command."""
        self.player.make_move("down")

    def do_right(self, arg):
        """Process 'right' command."""
        self.player.make_move("right")

    def do_left(self, arg):
        """Process 'left' command."""
        self.player.make_move("left")

    def do_addmon(self, arg):
        """
        Process 'addmon' command.

        And check correctness of given arguments
        """
        options = shlex.split(arg)
        if len(options) != 8:
            clients_queue[self.id].put_nowait("Invalid arguments")
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
                        clients_queue[self.id].put_nowait('Invalid arguments')
                        err_flag = True
                        break
                    if not (hp > 0):
                        clients_queue[self.id].put_nowait('Invalid arguments')
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
                        clients_queue[self.id].put_nowait('Invalid arguments')
                        err_flag = True
                        break
                    if not (0 <= x <= Field.size and 0 <= y <= Field.size):
                        clients_queue[self.id].put_nowait('Invalid arguments')
                        err_flag = True
                        break
                    opt_set.add('coords')
                    param_dict['coords'] = (x, y)
                    i += 3
                case _:
                    clients_queue[self.id].put_nowait('Invalid arguments')
                    err_flag = True
                    return
        if err_flag:
            return
        if opt_set != {'hello', 'hp', 'coords'}:
            clients_queue[self.id].put_nowait('Invalid arguments')
            return
        field.add_monster(x, y, Monster(**param_dict), self.id)

    def do_attack(self, arg):
        """Process 'attack' command."""
        arg = shlex.split(arg)
        weapon = 'sword'
        if len(arg) == 1:
            self.player.attack(arg[0], weapon)
        elif len(arg) == 3:
            match arg[1:]:
                case ['with', arms]:
                    if arms not in self.player.get_weapons():
                        clients_queue[self.id].put_nowait("Unknown weapon")
                    else:
                        self.player.attack(arg[0], arms)
                case _:
                    clients_queue[self.id].put_nowait("Invalid arguments")
                    return
        else:
            clients_queue[self.id].put_nowait("Invalid arguments")
            return

    def do_sayall(self, arg):
        """Process 'sayall' command."""
        self.player.sayall(arg)

    def do_EOF(self, arg):
        """If EOF is seen, return 1."""
        return 1


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

field = Field()

clients = {}                        # client_id to client's Player class
clients_names = set()
clients_queue = {}                  # client_id to client_queue
broadcast_queue = {}


async def play(reader, writer):
    """
    When another player has connected, this function is invoked.

    Register client, check if given login is unique, create asyncio tasks
    for sending, receiving and broadcasting data
    When connection is lost, delete all data associated with left client
    """
    client_id = "{}:{}".format(*writer.get_extra_info('peername'))
    print("LOG: new client connected with id", client_id)
    clients_queue[client_id] = asyncio.Queue()
    broadcast_queue[client_id] = asyncio.Queue()
    receive_data_from_client = asyncio.create_task(reader.readline())
    write_data_to_client = asyncio.create_task(clients_queue[client_id].get())
    broadcast_task = asyncio.create_task(broadcast_queue[client_id].get())
    await writer.drain()

    login_name, pending = await asyncio.wait([receive_data_from_client],
                                             return_when=asyncio.FIRST_COMPLETED)
    name = login_name.pop().result().decode().strip()
    if name not in clients_names:
        clients[client_id] = Player(field, client_id, name)
        clients_names.add(name)
        msg = f"{name} has joined the field"
        await broadcast_queue[client_id].put(msg)
    else:
        msg = f"You are an impostor, {name}!\nGet outta here"
        writer.write(msg.encode())
        receive_data_from_client.cancel()
        write_data_to_client.cancel()
        broadcast_task.cancel()
        clients_names.remove(name)
        del clients_queue[client_id]
        del clients[client_id]
        writer.close()
        await writer.wait_closed()
        return

    shell = MUD_shell(clients[client_id])

    receive_data_from_client = asyncio.create_task(reader.readline())
    while not reader.at_eof():
        done, pending = await asyncio.wait([receive_data_from_client,
                                            write_data_to_client,
                                            broadcast_task],
                                           return_when=asyncio.FIRST_COMPLETED)
        for q in done:
            if q is receive_data_from_client:
                receive_data_from_client = asyncio.create_task(reader.readline())
                data = q.result().decode().strip()
                try:
                    shell.onecmd(data)
                except Exception as e:
                    print("LOG: while handling user's command exception occure\n", e)
                    await clients_queue[client_id].put("Something wrong with command")
            elif q is write_data_to_client:
                data = q.result()
                while not clients_queue[client_id].empty():
                    data += '\n' + clients_queue[client_id].get_nowait()
                write_data_to_client = asyncio.create_task(clients_queue[client_id].get())
                writer.write((data).encode())
            elif q is broadcast_task:
                data = q.result()
                while not broadcast_queue[client_id].empty():
                    data += '\n' + broadcast_queue[client_id].get_nowait()
                broadcast_task = asyncio.create_task(broadcast_queue[client_id].get())
                for id in clients:
                    client_queue = clients_queue[id]
                    await client_queue.put(data)
            await writer.drain()

    print(f"LOG: {name} disconnected")
    receive_data_from_client.cancel()
    write_data_to_client.cancel()
    broadcast_task.cancel()
    clients_names.remove(name)
    del clients_queue[client_id]
    del clients[client_id]
    writer.close()
    await writer.wait_closed()


async def moving_monster_daemon():
    """Daemon which invokes :meth:`Field.wandering_monster` for moving one random monster."""
    while True:
        print("LOG: invoked daemon for moving monsters")
        field.wandering_monster()
        await asyncio.sleep(10)


async def main():
    """Create server, start daemon."""
    print("LOG: starting server")
    server = await asyncio.start_server(play, '0.0.0.0', 1337)
    daemon = asyncio.create_task(moving_monster_daemon())
    await asyncio.sleep(0)
    async with server:
        await server.serve_forever()
