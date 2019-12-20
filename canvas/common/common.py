import decimal
import itertools


def drange(x, y, jump):
    while x < y:
        yield float(x)
        x += decimal.Decimal(jump)


def split_every(iterable, n):
    i = iter(iterable)
    slice = list(itertools.islice(i, n))
    while slice:
        yield slice
        slice = list(itertools.islice(i, n))


def twod_to_oned(size, *coordinates):
    """Converts coordinates (x >= 0, y >= 0) to an int representation.
    :param size: Size of the grid that (x, y) is contained in
    :param coordinates: [(x0, y0), (x1,  y1), ...]
    :return: (int0, int1, ...)
    """
    x_axis = size[0]
    result = tuple(x + y * x_axis for x, y in coordinates)
    if len(result) == 1:
        return result[0]
    return result


def flatten(iterable, iterations: int=1):
    if isinstance(iterable[0], int) or isinstance(iterable[0], str):
        return iterable
    for _ in range(iterations):
        iterable = sum(iterable, iterable[0].__class__())
    return iterable


def flap(arg, functions):
    for function in functions:
        arg = function(arg)
    return arg


def intercept(intercept: float, iterable):
    return iterable[int(intercept * (len(iterable) - 1))]

def unique_permutations(iterable):
    results = []
    for r in range(len(iterable)):
        for permutation in itertools.permutations(iterable, r):
            permutation = sorted(permutation)
            if permutation not in results:
                yield permutation
                results.append(permutation)
