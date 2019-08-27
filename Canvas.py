from __future__ import annotations

import math
from collections import abc
from itertools import chain
from functools import wraps
from PIL import Image
from typing import Type

from common import common, sili_math, line_thingy


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
    def from_pillow(cls, im: Image.Image):
        return cls(im.getdata(), im.size)

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


class ClosedCanvas(Canvas, NoneIsImmutableTuple):
    def __setitem__(self, key, value):
        try:
            key = common.twod_to_oned(self.size, key)
        except TypeError:
            pass
        super().__setitem__(key, value)


class CanvasLayer(Canvas):
    def __init__(self, canvas: Canvas or Type[Canvas]):
        self.c = canvas
        super().__init__(self.c.data, self.c.size)

    def __setitem__(self, key, value):
        try:
            key = common.twod_to_oned(self.size, key)
        except TypeError:
            pass
        if not self.c.is_excluded(key):
            return
        super().__setitem__(key, value)

    def save(self):
        """Overwrites self._c.data with self.data
        """
        self.c.data = self.data


class CanvasAbstraction(CanvasLayer):
    def exclude(self, positions):
        for position in positions:
            if self.is_excluded(position):
                self.data[position] = None

    def unexclude(self, positions):
        for position in positions:
            if not self.is_excluded(position):
                self.data[position] = self.c.data[position]

    def save(self):
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


class SimpleCanvasAbstraction(CanvasAbstraction):
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


class CanvasController(CanvasLayer):
    """Allows the creation of canvases within a canvas
    Which can allow tessellation or fractal patterns
    """
    def __init__(self, canvas):
        super().__init__(canvas)
        self.canvases = []

    def bbox_is_outside_range(self, bbox):
        pos0, pos1 = bbox
        x0, y0 = pos0
        x1, y1 = pos1

        outside_range = False
        if any(x < 0 or x > self.width for x in (x0, x1)) \
                or any(y < 0 or y > self.length for y in (y0, y1)):
            outside_range = True
        return outside_range

    def _outside_range(self, bbox):
        if not self.bbox_is_outside_range:
            return self.portion(bbox)

        pos0, pos1 = bbox
        x0, y0 = pos0
        x1, y1 = pos1

        size = x1 - x0 + 1, y1 - y0 + 1
        canvas = Canvas.from_empty_size(size)
        self.canvases.append((canvas, bbox[0]))

        positions = []
        for pos in sili_math.positions_within(bbox):
            try:
                i = self.c[pos]
            except IndexError:
                i = None

            positions.append(i)
        canvas.putdata(positions)

        return canvas

    def portion(self, bbox):
        if self.bbox_is_outside_range:
            return self._outside_range(bbox)

        gridded_data = shapes.quadrilateral.portion(self.c.as_grid(), *bbox)
        canvas = Canvas(common.flatten(gridded_data), (bbox[1][0] - bbox[0][0], bbox[1][1] - bbox[0][1]))
        self.canvases.append((canvas, bbox[0]))
        return canvas

    def unscope(self, idx):
        self.c.insert(*self.canvases.pop(idx))

    def unscope_all(self):
        [self.unscope(0) for _ in range(len(self.canvases))]

    def get_canvases(self):
        yield from self.canvases

    def _portion_from_rangeable(self, size, x_positions, y_positions):
        for j, y_pos in enumerate(y_positions):
            for x_pos in x_positions:
                bbox0 = x_pos, y_pos
                bbox1 = sili_math.get_opposite_corner(bbox0, size)
                yield self.portion((bbox0, bbox1))

    def fragment(self, size, width_padding: int=0, length_padding: int=0):
        x_positions = [*line_thingy.padded_maximum(self.width, width_padding, size[0])]
        y_positions = line_thingy.padded_maximum(self.length, length_padding, size[1])
        yield from self._portion_from_rangeable(size, x_positions, y_positions)

    def fragment_fill_in(self, size, sizes_per_width: int, sizes_per_length: int):
        x_positions = [*line_thingy.fill_in_shortcut(self.width, size[0], sizes_per_width)]
        y_positions = line_thingy.fill_in_shortcut(self.length, size[1], sizes_per_length)
        yield from self._portion_from_rangeable(size, x_positions, y_positions)

