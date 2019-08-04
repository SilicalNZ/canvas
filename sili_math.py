from functools import reduce
from operator import mul


def prod(iterable):
    return reduce(mul, iterable, 1)


def split_num(x: int):
    a, b = divmod(x, 2)
    if b:
        b, a = a, a + 1
    else:
        b = a
    return a, b


def cheap_round(x: float):
    return int(x + 0.5)
