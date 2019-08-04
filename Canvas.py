from copy import copy

from PIL import Image

from shapes import quadrilateral

n_set = set

# Requires an iterable
def _iterable_split(iterable, width: int):
    """Yield successive n-sized chunks from l."""
    iterable = list(iterable)
    link = []
    for i in range(0, len(iterable), width):
        link.append(tuple(iterable[i:i + width]))
    return tuple(link)


def _iterable_overwrite(iterable_old, iterable_new):
    old_length, new_length = len(iterable_old), len(iterable_new)

    if new_length == old_length:
        return tuple(iterable_new)
    elif new_length > old_length:
        return tuple(list(iterable_new)[:old_length])
    elif old_length > new_length:
        return tuple(list(iterable_new) + (list(iterable_old)[new_length:]))


def _iterable_remove_nested(iterable, iterations: int=1):
    if isinstance(iterable[0], int) or isinstance(iterable[0], str):
        return iterable
    for _ in range(iterations):
        iterable = sum(iterable, iterable[0].__class__())
    return iterable


as_grid = _iterable_split


def _oned_to_twod(size, positions):
    x_axis, y_axis = size
    return [(int(i % x_axis), i // y_axis) for i in positions]


def _twod_to_oned(size, coordinates):
    x_axis = size[0]
    return tuple(x + y * x_axis for x, y in coordinates)


def _find_bbox(coordinates):
    coordinates = tuple(coordinates)

    y_axis = lambda y: y[1]
    x_axis = lambda x: x[0]

    pos0 = min(coordinates, key=x_axis)[0], min(coordinates, key=y_axis)[1]
    pos1 = max(coordinates, key=x_axis)[0] + 1, max(coordinates, key=y_axis)[1] + 1

    return pos0, pos1


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


class Canvas(SizeInfo):
    def __init__(self, iterable, width):
        self.data = tuple(iterable)
        get_size = _iterable_split(self.data, width)
        super().__init__((len(get_size[0]), len(get_size)))

    def get_positions(self):
        return range(len(self.data))

    def getxy(self):
        res = []
        for y, i in enumerate(_iterable_split(self.data, self.width)):
            for x, j in enumerate(i):
                res.append((x, y))
        return res

    def getdata(self):
        return [i for i in self.data if i is not None]

    def putdata(self, iterable):
        org_type = self.data.__class__
        data = list(self.data)
        iterable = iter(iterable)
        for x, i in enumerate(data):
            if i is not None:
                try:
                    i = next(iterable)
                except StopIteration:
                    return
                else:
                    data[x] = i
        self.data = org_type(data)

    @classmethod
    def from_pillow(cls, im: Image.Image):
        return cls(im.getdata(), im.width)

    @classmethod
    def from_canvas(cls, canvas):
        return cls(canvas, canvas.width)

    def __copy__(self):
        return self.__class__(self.data, self.width)

    @property
    def excluded(self):
        """Returns the index of excluded cells"""
        return [x for x, i in enumerate(self.data) if i is None]

    @property
    def unexcluded(self):
        """Returns the index of not excluded cells"""
        return [x for x, i in enumerate(self.data) if i is not None]

    def range(self):
        return range(len(self.data))

    def rearrange(self, func):
        self.putdata(func(self.getdata()))


class ExcludableCanvas(Canvas):
    def __init__(self, iterable, width):
        super().__init__(iterable, width)
        self.data = list(self.data)
        self.org_data = tuple(self.data)

    def are_excluded(self, positions):
        return set(self.excluded).intersection(positions)

    def are_unexcluded(self, positions):
        return set(self.unexcluded).intersection(positions)

    def exclude(self, positions):
        for position in self.are_unexcluded(positions):
            self.data[position] = None

    def unexclude(self, positions):
        for position in self.are_excluded(positions):
            self.data[position] = self.org_data[position]

    def remove_excluded(self):
        self.unexclude(self.range())

    def remove_unexcluded(self):
        self.exclude(self.range())

    def save(self):
        """Overwrites self.org_data with self.data
        """
        self.remove_excluded()
        self.org_data = tuple(self.data)

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
        self.save()
        self.exclude(unexcluded)


class _CanvasBase:
    def __init__(self, canvas: ExcludableCanvas):
        if hasattr(canvas, 'c'):
            self.c = c
        else:
            self.c = canvas


class ExcludableShortcuts(_CanvasBase):
    # _iterable_remove_nested just makes function writing a bit more versatile

    def _apply_to(self, function, attribute):
        getattr(self.c, attribute)(_iterable_remove_nested(tuple(function(as_grid(self.c.get_positions(), self.c.width)))))

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

    def rearrange(self, function):
        self.c.rearrange(function)

    def remove_excluded(self):
        self.c.remove_excluded()

    def remove_unexcluded(self):
        self.c.remove_unexcluded()

    def invert(self):
        self.c.invert()







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
    c = ExcludableCanvas.from_pillow(im)
    canvas = ExcludableShortcuts(c)
    canvas.difference(shapes.circle)
    canvas.rearrange(sorters.yiq)
    canvas.remove_excluded()

    image_res(list(canvas.c.data), canvas.c.size)






