from __future__ import annotations

from functools import wraps

from .BaseClasses import NoneIsImportantTuple, SizeInfo
from .common import *


def _coord_convertor(func):
    @wraps(func)
    def wrapper(self, key, *args, **kwargs):
        try:
            new_key = common.twod_to_oned(self.size, key)
        except TypeError:
            pass
        else:
            if key[0] < 0 or key[0] > self.width - 1 or key[1] < 0 or key[1] > self.length - 1:
                raise IndexError
            key = new_key
        return func(self, key, *args, **kwargs)
    return wrapper


class Canvas(NoneIsImportantTuple, SizeInfo):
    def __init__(self, data, size):
        NoneIsImportantTuple.__init__(self, data)
        SizeInfo.__init__(self, size)

    @_coord_convertor
    def __setitem__(self, key, value):
        super().__setitem__(key, value)

    @_coord_convertor
    def __getitem__(self, key):
        return super().__getitem__(key)

    @classmethod
    def from_empty_size(cls, size):
        return cls([0] * sili_math.prod(size), size)

    @classmethod
    def from_canvas(cls, canvas):
        return cls(canvas.data, canvas.size)

    def as_grid(self):
        return tuple(common.split_every(self.data, self.width))

    def insert(self, canvas: Canvas, corner):
        for y, length in enumerate(canvas.as_grid(), corner[1]):
            for x, width in enumerate(length, corner[0]):
                if width is None:
                    pass
                try: self[(x, y)] = width
                except IndexError:
                    pass
