from . import Canvas
from .common import *

class ScopedCanvas(Canvas):
    def __init__(self, canvas: Canvas or Type[Canvas]):
        self.c = canvas
        super().__init__(self.c.data, self.c.size)

    def unscope(self):
        raise NotImplemented()


class PositionalLayer(ScopedCanvas):
    def exclude(self, positions):
        for position in positions:
            if self.is_excluded(position):
                self.data[position] = None

    def unexclude(self, positions):
        for position in positions:
            if not self.is_excluded(position):
                self.data[position] = self.c.data[position]

    def unscope(self):
        self.c.putdata(self, 1)

    def remove_excluded(self):
        self.unexclude(range(len(self.data)))

    def remove_unexcluded(self):
        self.exclude(range(len(self.data)))

    def difference(self, positions):
        """This allows the difference of different shapes and algorithms
        Ex: A circle & triangle, will have the area of where they don't overlap
        """
        positions = set(self.unexcluded).difference(positions)
        self.remove_unexcluded()
        self.unexclude(positions)

    def union(self, positions):
        """This allows the mixing of different shapes and algorithms
        Ex: A circle & triangle, will have the area of both combined
        """
        self.unexclude(set(self.unexcluded).union(positions))

    def intersection(self, positions):
        """This allows the mixing of different shapes and algorithms
        Ex: A circle & triangle, will have the area of where they overlap
        """
        positions = set(self.unexcluded).intersection(positions)
        self.remove_unexcluded()
        self.unexclude(positions)

    def invert(self):
        unexcluded = self.unexcluded
        self.remove_excluded()
        self.exclude(unexcluded)


class Layer(PositionalLayer):
    # _iterable_remove_nested just makes function writing a bit more versatile

    def _apply_to(self, functions, attribute):
        grid = tuple(common.split_every(self.c.get_positions(), self.c.width))
        getattr(super(), attribute)(common.flatten(common.flap(grid, functions)))

    def difference(self, *functions):
        """This allows the difference of different shapes and algorithms
        Ex: A circle & triangle, will have the area of where they don't overlap
        """
        self._apply_to(functions, 'difference')

    def union(self, *functions):
        """This allows the mixing of different shapes and algorithms
        Ex: A circle & triangle, will have the area of both combined
        """
        self._apply_to(functions, 'union')

    def intersection(self, *functions):
        """This allows the mixing of different shapes and algorithms
        Ex: A circle & triangle, will have the area of where they overlap
        """
        self._apply_to(functions, 'intersection')

    def shape_and_rearrange(self, shape_func, rearrange_func):
        self.intersection(shape_func)
        self.rearrange(rearrange_func)
        self.remove_excluded()
