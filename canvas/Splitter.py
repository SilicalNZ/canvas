from typing import Type

from . import Canvas
from .common import *
from .BaseClasses import SizeInfo


class Splitter(SizeInfo):
    """Allows the creation of canvases within a canvas
    Which can allow tessellation or fractal patterns
    """
    def __init__(self, canvas):
        self.c = canvas
        super().__init__(self.c.size)
        self.canvases = []

    def bbox_is_outside_range(self, bbox):
        x0, x1, y0, y1 = bbox

        outside_range = False
        if any(x < 0 or x > self.width for x in (x0, x1)) \
                or any(y < 0 or y > self.length for y in (y0, y1)):
            outside_range = True
        return outside_range

    def _outside_range(self, bbox) -> Type[Canvas]:
        if not self.bbox_is_outside_range:
            return self.portion(bbox)

        x0, y0, x1, y1 = bbox

        size = x1 - x0 + 1, y1 - y0 + 1
        canvas = self.c.__class__.from_empty_size(size)
        self.canvases.append((canvas, bbox[:2]))

        positions = []
        for pos in sili_math.positions_within(bbox):
            try:
                i = self.c[pos]
            except IndexError:
                i = None

            positions.append(i)
        canvas.putdata(positions)

        return canvas

    def portion(self, bbox) -> Type[Canvas]:
        if self.bbox_is_outside_range:
            return self._outside_range(bbox)

        gridded_data = shapes.quadrilateral.portion(self.c.as_grid(), *bbox)
        canvas = self.c.__class__(common.flatten(gridded_data), (bbox[0] - bbox[1], bbox[2] - bbox[3]))
        self.canvases.append((canvas, bbox[:2]))
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
                yield self.portion((*bbox0, *bbox1))

    def fragment(self, size, width_padding: int=0, length_padding: int=0):
        x_positions = [*line_thingy.padded_maximum(self.width, width_padding, size[0])]
        y_positions = line_thingy.padded_maximum(self.length, length_padding, size[1])
        yield from self._portion_from_rangeable(size, x_positions, y_positions)

    def fragment_fill_in(self, size, sizes_per_width: int, sizes_per_length: int):
        x_positions = [*line_thingy.fill_in_shortcut(self.width, size[0], sizes_per_width)]
        y_positions = line_thingy.fill_in_shortcut(self.length, size[1], sizes_per_length)
        yield from self._portion_from_rangeable(size, x_positions, y_positions)

    def crack(self, sizes_per_width: int=1, sizes_per_length: int=1):
        x_positions = [*line_thingy.find_fill_in(self.width, sizes_per_width)]
        y_positions = line_thingy.find_fill_in(self.length, sizes_per_length)
        for y_pos, length in y_positions:
            for x_pos, width in x_positions:
                bbox0 = x_pos, y_pos
                bbox1 = sili_math.get_opposite_corner(bbox0, (width, length))
                yield self.portion((*bbox0, *bbox1))
