import unittest
import prog


class TestProg(unittest.TestCase):
    def test_0_prog(self):
        self.assertEqual(prog.sqroots("1 2 3"), "")

    def test_1_prog(self):
        self.assertEqual(prog.sqroots("1 -1 -6"), "-2.0 3.0")

    def test_2_prog(self):
        self.assertEqual(prog.sqroots("1 2 1"), "-1.0")

    def test_exception_prog(self):
        with self.assertRaises(Exception):
            prog.sqroots("0 0 0")
