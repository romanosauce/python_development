"""Module to print name array."""


def some_func(name):
    """This is a function."""
    return [f"{name}{i} {j}" for i in range(10) for j in range(10)]

print(some_func('Roma'))
