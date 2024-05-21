import unittest
import socket
import multiprocessing
import asyncio
import mood.server as server
import sys
import time


def send_and_receive_command(cmd, socket):
    socket.sendall((cmd + '\n').encode())
    response = socket.recv(1024).decode().strip()
    return response


def start_server():
    sys.stdout = open('/dev/null', 'w')
    asyncio.run(server.main())


class TestClientServerCommands(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proc = multiprocessing.Process(
                target=start_server)
        cls.proc.start()
        time.sleep(0.01)
        cls.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cls.s.connect(('localhost', 1337))
        cls.s.sendall(('TESTING\n').encode())
        cls.s.recv(1024)
        cls.s.sendall(("movemonsters off\n").encode())
        cls.s.recv(1024)

    def test_1_addmon(self):
        response = send_and_receive_command('addmon kiss 0 1 "aa bb" 10', self.s)
        self.assertEqual(response, 'TESTING added monster kiss to (0, 1) saying aa bb with 10 hps')

    def test_2_move_encounter(self):
        response = send_and_receive_command('move 0 1', self.s)
        ans = r'''Moved to (0, 1)
 _______ 
< aa bb >
 ------- 
     \
      \
             ,;;;;;;;,
            ;;;;;;;;;;;,
           ;;;;;'_____;'
           ;;;(/))))|((\
           _;;((((((|))))
          / |_\\\\\\\\\\\\
     .--~(  \ ~))))))))))))
    /     \  `\-(((((((((((\\
    |    | `\   ) |\       /|)
     |    |  `. _/  \_____/ |
      |    , `\~            /
       |    \  \           /
      | `.   `\|          /
      |   ~-   `\        /
       \____~._/~ -_,   (\
        |-----|\   \    ';;
       |      | :;;;'     \
      |  /    |            |
      |       |            |'''
        self.assertEqual(response, ans)

    def test_3_attack(self):
        response = send_and_receive_command('attack kiss sword', self.s)
        ans = '''TESTING attacked kiss with sword
causing 10 hps damage
kiss died'''
        self.assertEqual(response, ans)

    def test_4_locale(self):
        response = send_and_receive_command('locale ru_RU.UTF-8', self.s)
        ans = 'Установлена локаль: ru_RU.UTF-8'
        self.assertEqual(response, ans)

    def test_5_ru_attack(self):
        response = send_and_receive_command('addmon kiss  0 1 "aaa aaa" 21', self.s)
        ans = 'TESTING добавил монстра kiss в позицию (0, 1), говорящего aaa aaa имеющего 21 oчко здоровья'
        self.assertEqual(response, ans)

    @classmethod
    def tearDownClass(cls):
        cls.s.close()
        cls.proc.terminate()
