import shlex

name = input()
b_place = input()
print("register", shlex.quote(name), shlex.quote(b_place))
