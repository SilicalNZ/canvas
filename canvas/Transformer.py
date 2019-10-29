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
        items = {i: [] for i in set(self.c)}
        [items[i].append(x) for x, i in zip(self.get_positions(), self.c)]
        yield from [items[i].pop(0) if i is not None else None for i in self]

    def movement(self, function):
        yield from [function(*coords) if coords[0] is not None else None for coords in zip(self.get_positions(), self.how_did_it_transform())]

    def transition(self, function):
        yield from [function(*coords) if all(i is not None for i in coords) else None for coords in zip(self, self.data) ]


class Transformer:
    def __init__(self, canvases: Tuple[Type[Comparer], Type[Comparer]]):
        self.canvas0, self.canvas1 = [Tracker(canvas) if not isinstance(canvas, Tracker) else canvas for canvas in canvases]

    def _binder(self, intercept: float, function, attr):
        if not hasattr(self, f'_cache_{attr}'):
            data0 = getattr(self.canvas0, attr)()
            data1 = getattr(self.canvas1, attr)()

            binder = [[*function(*coords)] if all(i is not None for i in coords) else None for coords in zip(data0, data1)]
            setattr(self, f'_cache_{attr}', binder)

        yield from [common.intercept(intercept, i) for i in getattr(self, f'_cache_{attr}')]

    def movement(self, intercept: float, function):
        template = Canvas.from_empty_size(self.canvas0.size)
        for colour, coord in zip(self.canvas0, self._binder(intercept, function, 'how_did_it_transform')):
            if coord is not None:
                template[coord] = colour
        return template
