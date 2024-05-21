import unittest
import unittest.mock as mock
import mood.client as client
from io import StringIO


class TestClientCommandParsing(unittest.TestCase):
    def test_0_move_up(self):
        with (
                mock.patch('sys.stdin', StringIO("up")),
                mock.patch('socket.socket', autospec=True) as socket_mock,
                mock.patch('mood.client.msg_reciever', return_value=True)
             ):
            client.start_client("TESTING!")
            sendall_call = socket_mock.mock_calls[4].args[0]
            self.assertEqual(sendall_call, b'move 0 -1\n')

    def test_1_move_down(self):
        with (
                mock.patch('sys.stdin', StringIO("down")),
                mock.patch('socket.socket', autospec=True) as socket_mock,
                mock.patch('mood.client.msg_reciever', return_value=True)
             ):
            client.start_client("TESTING!")
            sendall_call = socket_mock.mock_calls[4].args[0]
            self.assertEqual(sendall_call, b'move 0 1\n')

    def test_2_attack_default(self):
        command = "addmon kiss coords 0 1 hello eww hp 10\ndown\nattack kiss"
        with (
                mock.patch('sys.stdin', StringIO(command)),
                mock.patch('socket.socket', autospec=True) as socket_mock,
                mock.patch('mood.client.msg_reciever', return_value=True)
             ):
            client.start_client("TESTING!")
            sendall_call = socket_mock.mock_calls[6].args[0]
            self.assertEqual(sendall_call, b'attack kiss sword\n')

    def test_3_attack_axe(self):
        command = "addmon kiss coords 0 1 hello eww hp 10\ndown\nattack kiss with axe"
        with (
                mock.patch('sys.stdin', StringIO(command)),
                mock.patch('socket.socket', autospec=True) as socket_mock,
                mock.patch('mood.client.msg_reciever', return_value=True)
             ):
            client.start_client("TESTING!")
            sendall_call = socket_mock.mock_calls[6].args[0]
            self.assertEqual(sendall_call, b'attack kiss axe\n')

    def test_4_attack_wrong_weapon(self):
        command = "addmon kiss coords 0 1 hello eww hp 10\ndown\nattack kiss with alibarda"
        with (
                mock.patch('sys.stdin', StringIO(command)),
                mock.patch('builtins.print', autospec=True) as output_mock,
                mock.patch('socket.socket', autospec=True),
                mock.patch('mood.client.msg_reciever', return_value=True)
             ):
            client.start_client("TESTING!")
            output_call = output_mock.mock_calls[0].args[0]
            self.assertEqual(output_call, 'Unknown weapon\n>>> ')
