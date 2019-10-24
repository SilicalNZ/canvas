from . import Canvas, Splitter
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

    def fill_in(self, distance: int):
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
