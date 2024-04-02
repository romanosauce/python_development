import cowsay
import io
import shlex
import sys
import cmd
import socket
import asyncio
import queue


class Field:
    size = 10

    def __init__(self):
        self.field = [[0 for i in range(self.size)] for j in range(self.size)]
        self.monsters_pos = {}

    def add_monster(self, x, y, monster, id):
        if monster.get_name() in cowsay.list_cows() or \
                monster.get_name() in cows_dict:
            if monster.get_name() in cows_dict:
                monster.set_custom(True)
            subst = False
            if (x, y) in self.monsters_pos:
                subst = True
            self.monsters_pos[(x, y)] = monster
            msg = f"{clients[id][0]} added monster {monster.get_name()} to ({x}, {y}) saying {monster.get_phrase()}"
            broadcast_queue[id].put_nowait(msg)
            if subst:
                broadcast_queue[id].put_nowait("Replaced the old monster")
        else:
            clients_queue[id].put_nowait("Cannot add unknown monster")

    def delete_mon(self, coords):
        self.monsters_pos.pop(coords)

    def get_monster(self, pos):
        return self.monsters_pos[pos]

    def get_monsters_pos(self):
        return self.monsters_pos.keys()

    def encounter(self, x, y, id):
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


class Player:
    _dir_dict = {"up": (0, -1), "down": (0, 1),
                 "left": (-1, 0), "right": (1, 0)}

    weapons = {"sword": 10, "spear": 15, "axe": 20}

    def __init__(self, field, id, name):
        self.x = 0
        self.y = 0
        self.field = field
        self.id = id
        self.name = name

    def get_weapons(self):
        return self.weapons

    def make_move(self, side):
        dirs = self._dir_dict[side]
        self.x += dirs[0]
        self.y += dirs[1]
        self.x %= Field.size
        self.y %= Field.size
        clients_queue[self.id].put_nowait(f"Moved to ({self.x}, {self.y})")
        self.field.encounter(self.x, self.y, self.id)

    def attack(self, name, weapon):
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
        broadcast_queue[self.id].put_nowait(msg)


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

    def get_damage(self, damage, id):
        if damage < self.hp:
            self.hp -= damage
            broadcast_queue[id].put_nowait(f"{self.name} now has {self.hp}")
        else:
            broadcast_queue[id].put_nowait(f"{self.name} died")
            field.delete_mon(self.coords)


class MUD_shell(cmd.Cmd):
    def __init__(self, player_info):
        self.player = player_info[1]
        self.id = player_info[0]

    def do_up(self, arg):
        self.player.make_move("up")

    def do_down(self, arg):
        self.player.make_move("down")

    def do_right(self, arg):
        self.player.make_move("right")

    def do_left(self, arg):
        self.player.make_move("left")

    def do_addmon(self, arg):
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
            print(6)
            clients_queue[self.id].put_nowait('Invalid arguments')
            return
        field.add_monster(x, y, Monster(**param_dict), self.id)

    def do_attack(self, arg):
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
        self.player.sayall(arg)

    def do_EOF(self, arg):
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

clients = {}                        # client_id to client's login and Player class
clients_names = set()
clients_queue = {}                  # client_id to client_queue
broadcast_queue = {}


async def play(reader, writer):
    client_id = "{}:{}".format(*writer.get_extra_info('peername'))
    print(client_id)
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
        clients[client_id] = [name, Player(field, client_id, name)]
        clients_names.add(name)
        msg = f"{name} has joined the field"
        await broadcast_queue[client_id].put(msg)
    else:
        msg = f"You are an impostor, {name}!\nGet outta here"
        writer.write(msg.encode())
        return

    shell = MUD_shell((client_id, clients[client_id][1]))

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
                except Exception:
                    await clients_queue[client_id].put("Something wrong with command")
            elif q is write_data_to_client:
                write_data_to_client = asyncio.create_task(clients_queue[client_id].get())
                data = q.result()
                writer.write((data).encode())
            elif q is broadcast_task:
                data = q.result()
                while not broadcast_queue[client_id].empty():
                    data += ' ' + broadcast_queue[client_id].get_nowait()
                broadcast_task = asyncio.create_task(broadcast_queue[client_id].get())
                for id in clients:
                    client_queue = clients_queue[id]
                    await client_queue.put(data)
            await writer.drain()

    print(f"{name} disconnected")
    receive_data_from_client.cancel()
    write_data_to_client.cancel()
    broadcast_task.cancel()
    clients_names.remove(clients[client_id][0])
    del clients_queue[client_id]
    del clients[client_id]
    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(play, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

asyncio.run(main())
