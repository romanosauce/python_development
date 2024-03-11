import cmd


class Echoer(cmd.Cmd):
    """Dumb echo command REPL"""
    prompt = ":->"
    words = "one", "two", "four", "five"

    def do_echo(self, arg):
        print(arg)

    def complete_echo(self, text, line, begidx, endidx):
        return [c for c in self.words if c.startswith(text)]

    def do_EOF(self, arg):
        return True

    def emptyline(self):
        pass


if __name__ == "__main__":
    Echoer().cmdloop()
