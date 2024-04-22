import math


def sqroots(coefs: str):
    coefs = list(map(float, coefs.split()))
    a, b, c = coefs
    d = b**2 - 4 * a * c
    if d < 0:
        return ""
    sol1 = (-b - math.sqrt(d))/(2 * a)
    sol2 = (-b + math.sqrt(d))/(2 * a)
    if sol1 == sol2:
        return str(sol1)
    return str(sol1) + ' ' + str(sol2)
