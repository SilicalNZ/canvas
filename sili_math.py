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


def positions_within(bbox):
    pos0, pos1 = bbox
    x0, y0 = pos0
    x1, y1 = pos1

    for y in range(y0, y1 + 1, 1):
        for x in range(x0, x1 + 1, 1):
            yield (x, y)
