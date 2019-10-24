from collections import abc
from typing import Type


class SizeInfo:
    def __init__(self, size):
        self.size = size

    @property
    def size_sum(self):
        return self.width * self.length

    @property
    def width(self):
        return self.size[0]

    @property
    def length(self):
        return self.size[1]


class IndexableTuple(abc.Sequence):
    def __init__(self, data):
        self.data = list(data)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        yield from iter(self.data)

    def __contains__(self, item):
        return item in self.data

    def __reversed__(self):
        return self.__class__(reversed(self.data))

    def reverse(self):
        self.data.reverse()

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __repr__(self):
        return repr(tuple(self.data))


class NoneIsImportantTuple(IndexableTuple):
    def putdata(self, iterable, option: int=0):
        """
        :param iterable: an iterable of unimportant length
        :param option:
            0 = Will jump past None indexes
            1 = Will not jump past None
        :return:
        """
        if option == 0:
            iterable = iter(iterable)
            for x, i in enumerate(self.data):
                if i is None:
                    continue
                try:
                    i = next(iterable)
                except StopIteration:
                    return
                else:
                    self[x] = i
        elif option == 1:
            for x, i in enumerate(iterable):
                if i is None:
                    continue
                try:
                    self[x] = i
                except IndexError:
                    continue

    def get_positions(self):
        yield from range(len(self.data))

    def is_excluded(self, key):
        return bool(self[key])

    def getdata(self):
        return [i for i in self.data if i is not None]

    @property
    def excluded(self):
        """Returns the index of excluded cells"""
        return [x for x, i in enumerate(self) if i is None]

    @property
    def unexcluded(self):
        """Returns the index of not excluded cells"""
        return [x for x, i in enumerate(self) if i is not None]

    def rearrange(self, func):
        self.putdata(func(self.getdata()))

    @property
    def is_redundant(self):
        return len(self.excluded) == len(self)


class NoneIsImmutableTuple(NoneIsImportantTuple):
    def __setitem__(self, key, value):
        if self.data[key] is not None:
            self.data[key] = value
