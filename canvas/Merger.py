from itertools import permutations

from . import Canvas, Splitter
from .BaseClasses import CanvasNone
from .common import *

class Merger:
    def __init__(self, canvases):
        self.canvases = canvases
        self.alignment = None
        self.axis = 0

    @property
    def lengths(self):
        return [i.length for i in self.canvases]

    @property
    def widths(self):
        return [i.width for i in self.canvases]

    @property
    def sizes(self):
        return [i.size for i in self.canvases]

    @property
    def _inverted_axis(self):
        return abs(self.axis - 1)

    def _active_axis(self, invert=False):
        axes = {0: self.widths,
                1: self.lengths}
        if invert:
            return axes[self._inverted_axis]
        return axes[self.axis]

    def _active_alignment(self, segments):
        alignments = {0: lambda segments: tuple([0] * len(segments)),
                      1: line_thingy.align_centre,
                      2: line_thingy.align_right}

        return alignments[self.alignment](segments)

    def _realign(self):
        return self.alignments(self.axes[self.axis])

    def fill_in_lateral(self, distance: int = None, additive: int = 0):
        distance = distance if distance else sum(self._active_axis())
        distance += additive

        bbox0 = [list(i) for i in self.sizes]
        pos0 = line_thingy.fill_in_line(distance, self._active_axis())
        pos1 = self._active_alignment(self._active_axis(invert=True))
        for x, i in enumerate(zip(pos0, pos1)):
            i0, i1 = i
            bbox0[x][self.axis] = i0
            bbox0[x][self._inverted_axis] = i1

        bbox1 = [sili_math.get_opposite_corner(i, c.size) for i, c in zip(bbox0, self.canvases)]
        x = max([i[0] for i in bbox1])
        y = max([i[1] for i in bbox1])

        c = Canvas.from_empty_size((x, y))
        splitter = Splitter(c)
        [splitter.canvases.append((canvas, corner)) for canvas, corner in zip(self.canvases, bbox0)]
        return splitter

    def fill_in_canvas(self, canvas):
        if sum(map(sili_math.prod, self.sizes)) != sili_math.prod(canvas.size):
            raise IndexError('canvases cannot fit in canvas')

        _canvas = Canvas.from_empty_size(canvas.size, CanvasNone)

        def get_empty_spot(c: Canvas):
            for data, pos in c.data_and_positions():
                if data is CanvasNone:
                    return pos

        for i in permutations(self.canvases):
            temp = Canvas.from_canvas(_canvas)
            try:
                [temp.insert(j, get_empty_spot(temp), raise_error=True) for j in i]
            except IndexError:
                pass
            else:
                if CanvasNone not in temp:
                    yield temp

    def find_fill_in(self):
        for length in common.unique_permutations(self.lengths):
            length = sum(length)
            for width in common.unique_permutations(self.widths):
                width = sum(width)
                try:
                    yield from self.fill_in_canvas(Canvas.from_empty_size((width, length), default=CanvasNone))
                except IndexError:
                    pass
