import shlex

s = input()
print(shlex.join(shlex.split(s)))
