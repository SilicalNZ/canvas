from typing import Type, Tuple

from . import Canvas
from .common import *
from .Layer import Comparer

from .tools.geometry import TwoDimensional

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
        sequence = [items[i].pop(0) if i is not None else None for i in self]
        return Canvas(sequence, self.size)

    def movement(self, function):
        sequence = [function(*coords) if coords[0] is not None else None
                    for coords in zip(self.get_positions(), self.how_did_it_transform())]
        return Canvas(sequence, self.size)

    def transition(self, function):
        sequence = [function(*coords) if all(i is not None for i in coords) else None
                    for coords in zip(self.c, self)]
        return Canvas(sequence, self.size)


class Constructor:
    def __init__(self, canvas: Canvas, template: Canvas = None, pathways: Canvas = None, transforms: Canvas = None):
        self.c = canvas
        self.template = Canvas.from_canvas(self.c) if template is None else template
        self.pathways = pathways
        self.transforms = transforms

    def _gen_pathway(self, intercept: float):
        if self.pathways is None:
            yield from self.c.get_positions()
        else:
            yield from (common.intercept(intercept, pathway) for pathway in self.pathways)

    def _gen_transform(self, intercept: float):
        if self.transforms is None:
            yield from self.c
        else:
            yield from (common.intercept(intercept, transform) for transform in self.transforms)

    def intercept(self, intercept: float, overwrite_template = False) -> Canvas:
        template = Canvas.from_canvas(self.template)
        for x, transform in zip(self._gen_pathway(intercept), self._gen_transform(intercept)):
            if None not in (x, transform):
                template[x] = transform

        if overwrite_template:
            self.template = template
        return template
