from __future__ import annotations

from collections import abc
import itertools
import functools
from PIL import Image
from typing import Type


import common, sili_math


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
        import time
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


class NoneIsImmutableTuple(NoneIsImportantTuple):
    def __setitem__(self, key, value):
        if self.data[key] is not None:
            self.data[key] = value


class Canvas(NoneIsImportantTuple, SizeInfo):
    def __init__(self, data, size):
        NoneIsImportantTuple.__init__(self, data)
        SizeInfo.__init__(self, size)

    def __setitem__(self, key, value):
        try:
            new_key = common.twod_to_oned(self.size, key)
        except TypeError:
            pass
        else:
            if key[0] < 0 or key[0] > self.width or key[1] < 0 or key[1] > self.length:
                raise IndexError
            key = new_key
        super().__setitem__(key, value)

    @classmethod
    def from_pillow(cls, im: Image.Image):
        return cls(im.getdata(), im.size)

    @classmethod
    def from_canvas(cls, canvas):
        return cls(canvas.data, canvas.size)

    def as_grid(self):
        return tuple(common.split_every(self.data, self.width))

    def insert(self, canvas: Canvas, corner):
        for y, length in enumerate(canvas.as_grid(), corner[1]):
            for x, width in enumerate(length, corner[0]):
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

    def _apply_to(self, function, attribute):
        getattr(super(), attribute)(common.flatten(tuple(function(tuple(common.split_every(self.c.get_positions(), self.c.width))))))

    def difference(self, function):
        """This allows the difference of different shapes and algorithms
        Ex: A circle & triangle, will have the area of where they don't overlap
        """
        self._apply_to(function, 'difference')

    def union(self, function):
        """This allows the mixing of different shapes and algorithms
        Ex: A circle & triangle, will have the area of both combined
        """
        self._apply_to(function, 'union')

    def intersection(self, function):
        """This allows the mixing of different shapes and algorithms
        Ex: A circle & triangle, will have the area of where they overlap
        """
        self._apply_to(function, 'intersection')


class CanvasController(CanvasLayer):
    """Allows the creation of canvases within a canvas
    Which can allow tessellation or fractal patterns
    """
    def __init__(self, canvas):
        super().__init__(canvas)
        self.canvases = []

    def portion(self, bbox):
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


if __name__ == '__main__':
    import shapes, sorters


    def image_res(data, size):
        import time
        name = time.time()
        res = Image.new("RGB", size)
        res.putdata(data)
        res.save(f"test_images//output//{name}.png")
        return res


    im = Image.open('test_images//input//sili.png')
    c = Canvas.from_pillow(im)
    canvas = SimpleCanvasAbstraction(c)
    canvas.intersection(shapes.circle)
    canvas.rearrange(sorters.yiq)
    canvas.remove_excluded()
    canvas.save()

    control = CanvasController(c)
    here = control.portion(((0, 0), (control.c.width//2, control.c.length//2)))

    h = SimpleCanvasAbstraction(here)
    h.difference(shapes.triangle)
    h.rearrange(sorters.yiq)
    h.remove_excluded()
    h.save()
    control.unscope_all()

    image_res(canvas, im.size)

