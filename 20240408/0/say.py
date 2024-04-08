import cmd
import sys


class Say(cmd.Cmd):
    def do_bless(self, arg):
        print(arg)

    def do_sendto(self, arg):
        print(f"go to {arg}")

    def do_EOF(self, arg):
        return 1


if __name__ == '__main__':
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as file:
            saycmd = Say(stdin=file)
            saycmd.prompt = ''
            saycmd.use_rawinput = False
        saycmd.cmdloop()
    else:
        saycmd = Say()
        saycmd.cmdloop()
