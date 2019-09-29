from itertools import starmap
import math

from ..common import common, sili_math


def _middle_list(iterable, width: int):
    x = len(iterable)
    iterable = list(iterable)
    if x < width:
        return iterable
    i, j = sili_math.split_num(x)
    a, b = sili_math.split_num(width)

    return iterable[i - a: i + b]


def triangle(grid):
    width, length = len(grid[0]), len(grid)

    return list(starmap(_middle_list, zip(grid, map(int, common.drange(math.ceil(width / length), width + 1, width / length)))))


def vertical_lines(grid):
    return tuple(zip(*grid))


def _convertable(grid):
    res = []
    for y, i in enumerate(grid):
        for x, j in enumerate(i):
           res.append((x, y))
    return res


def circle(grid):
    width, length = len(grid[0]), len(grid)

    centre = min(sili_math.split_num(width)), min(sili_math.split_num(length))

    converts = _convertable(grid)
    find = lambda x, y, r: math.sqrt((x - centre[0])**2 + (y - centre[1])**2) <= r

    r = min(sili_math.split_num(min(width, length)))

    results = []
    for x, y in converts:
        the = find(x, y, r)
        if the:
            results.append(grid[y - 1][x - 1])
    return results


class quadrilateral:
    @staticmethod
    def portion(grid, pos0, pos1):
        width, length = len(grid[0]), len(grid)

        x0, y0 = pos0
        x1, y1 = pos1
        if x0 < 0 or y0 < 0 or x1 > width or y1 > length:
            raise IndexError('Region is outside of range')
        return [i[x0: x1] for i in grid[y0: y1]]

    @staticmethod
    def percentage(grid, percentage0: float, percentage1: float=None):
        if percentage1 is None:
            percentage1 = percentage0
        if percentage0 > 1 or percentage1 > 1:
            raise TypeError('An error here')
        width, length = len(grid[0]), len(grid)

        x, y = width * percentage0, length * percentage1
        x0, x1 = sili_math.split_num(int(x))
        y0, y1 = sili_math.split_num(int(y))

        return quadrilateral.portion(grid, (x0, y0), (x1, y1))
