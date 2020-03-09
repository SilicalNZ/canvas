import colorsys
import math
import pprint
import time
import statistics
from collections import Counter
import random

from canvas import *


def dist(a, b):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(a, b)))


class QuadTree:
    def __init__(self, template: Canvas, id, depth=1):
        self.id = id
        self.colour = None
        self.children = None
        self.template = template
        self.depth = depth
        self.parse_colour()
        self.traversed = False
        self.distance_from_parent = 0
        self.point = False

    @property
    def total_distance_from_parent(self):
        if self.children:
            return sum([i.total_distance_from_parent for i in self.children if not i.point])
        else:
            return self.distance_from_parent

    def parse_colour(self):
        bands = zip(*self.template)
        self.colour = tuple(int(statistics.mean(i)) for i in bands)

    def zoom(self):
        went_further = False

        if self.depth != 6:  # Important number
            self.parse_children()
            for child in self.children:
                child.distance_from_parent = dist(self.colour, child.colour)
                try:
                    child.zoom()
                except:
                    break
                else:
                    went_further = True

        if not went_further:
            self.children = None
        self.template = None

    def parse_children(self):
        splitter = Splitter(self.template)
        self.children = [QuadTree(i, x, depth=self.depth + 1) for x, i in enumerate(splitter.crack(2, 2))]

    def print(self, prefix=''):
        if self.children:
            for x, i in enumerate(self.children):
                print(prefix, x)
                i.print(prefix=prefix+'    ')


class Seedling:
    def __init__(self, c: Canvas):
        self.seed = QuadTree(c, 0)
        self.seed.zoom()
        self.c = Canvas.from_empty_size(c.size, self.seed.colour)
        self._c = c

    def unscope(self):
        self._c.pudata(self.c)

    def _navigate(self, template, nav, branch=None):
        # There is significant slowness when constantly splitting the canvas.
        #     Caching high regions of activity would be effective.
        if branch is None:
            branch = self.seed

        splitter = Splitter(template)
        te = [i for i in splitter.crack(2, 2)]

        t, i = te[nav[0]], branch.children[nav[0]]

        for tr, ir in zip(te, branch.children):
            if ir.traversed:
                continue
            else:
                res = [(0, 0, 0)] * tr.width
                [res.extend([(0, 0, 0)] + [ir.colour] * (tr.width - 2) + [(0, 0, 0)]) for _ in range(tr.length - 2)]
                res.extend([(0, 0, 0)] * tr.width)
                tr.putdata(res)
                ir.traversed = True

        if i.children and nav[1:]:
            try:
                self._navigate(t, nav[1:], i)
            except:
                i.point = True
        else:
            i.point = True

        splitter.unscope_all()

    def nav_location(self, pathway=None, max_depth=8):
        if pathway is None:
            pathway = [random.randint(0, 3) for _ in range(random.randint(max_depth-2, max_depth))]
        return self._navigate(self.c, pathway)

    def nav_importance(self, max_depth=8):
        def gather_distances(branch, nav=None):
            if not nav:
                nav = []
            if not branch.children:
                return

            dist = tuple(i.total_distance_from_parent if i.point is False else 0 for i in branch.children)

            dist = dist.index(max(dist))
            nav.append(dist)
            gather_distances(branch.children[dist], nav)
            return nav

        return self.nav_location(gather_distances(self.seed))


def example(canvas):
    sequence = []
    seed = Seedling(canvas)
    for i in range(100):
        now = time.time()
        print(i)
        seed.nav_importance(10)
        sequence.append(seed.c.as_PIL('RGB'))
        print('{:0.2f}'.format(time.time() - now))


    duration = [250] + [3 for _ in range(len(sequence) - 2)] + [250]
    sequence[0].save('result.gif',
                     format="gif",
                     save_all=True,
                     append_images=sequence[1:],
                     duration=duration,
                     loop=0)

    return seed.c
