import statistics


def simple(iterable):
    bands = zip(*iterable)
    return [tuple(int(statistics.mean(i)) for i in bands)] * len(iterable)


def replace(iterable, replacement):
    return (replacement for _ in range(len(iterable)))
