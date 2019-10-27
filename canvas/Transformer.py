from typing import Type, Tuple

from . import Canvas
from .common import *
from .Layer import Comparer

class Tracker(Comparer):
    def __init__(self, canvas: Type[Comparer]):
        super().__init__(canvas)

    def how_did_it_transform(self):
        """Gets the indexes of the new array as inplace indexes of the current image

        This only works when both states are unchanged with data and size.
            Order of data does not matter
        """
        items = {i: [] for i in set(self.data)}
        [items[i].append(x) for x, i in zip(self.get_positions(), self)]
        yield from [(x, items[i].pop(0)) if i is not None else None for x, i in zip(self.get_positions(), self.c)]

    def movement(self, function):
        yield from [function(*coords) for coords in self.how_did_it_transform()]

    def transition(self, function):
        yield from [function(*coords) for coords in zip(self, self.data) if all(i is not None for i in coords)]


class Transformer:
    def __init__(self, canvases: Tuple[Type[Comparer], Type[Comparer]]):
        self.canvas0, self.canvas1 = [Tracker(canavas) for canvas in canvases if not isinstance(canvas, Tracker)]

    def _binder(self, intercept: float, function, attr):
        if not hasattr(self, f'_cache_{attr}'):
            data0 = getattr(self.canvas0, attr)(function)
            data1 = getattr(self.canvas0, attr)(function)

            binder = [coords for coords in zip(data0, data1) if all(i is not None for i in coords)]
            setattr(self, attr, binder)

        yield from [common.intercept(intercept, i) for i in getattr(self, f'_cache_{attr}')]

    def movement(self, intercept: float, function):
        yield from self._binder(intercept, 'data_movement')
