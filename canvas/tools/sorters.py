import colorsys as _coloursys
from scipy.fftpack import hilbert as _hilbert
from functools import wraps, partial
import math
import random

_round = round


def _make_sorted(func):
    @wraps(func)
    def wrapper(iterable, *args, **kwargs):
        return sorted(iterable, key=partial(func, *args, **kwargs))
    return wrapper


@_make_sorted
def yiq(rgb):
    return _coloursys.rgb_to_yiq(*rgb)


def __hsv(rgb):
    return _coloursys.rgb_to_hsv(*rgb)
hsv = _make_sorted(__hsv)


@_make_sorted
def hls(rgb):
    return _coloursys.rgb_to_hls(*rgb)


def __step_sort(rgb, repetitions=8):
    r, g, b = rgb
    lum = math.sqrt(.241 * r + .691 * g + .068 * b)
    h, s, v = __hsv(rgb)

    h2 = int(h * repetitions)
    lum2 = int(lum * repetitions)
    v2 = int(v * repetitions)

    return h2, lum, v2

step_sort = _make_sorted(__step_sort)

@_make_sorted
def gradient_step_sort(rgb, repetitions=8):

    h2, lum, v2 = __step_sort(rgb, repetitions)
    if h2 % 2 == 1:
        v2 = repetitions - v2
        lum = repetitions - lum
    return h2, lum, v2


@_make_sorted
def hilbert(rgb):
    return tuple(_hilbert(rgb))


@_make_sorted
def round(rgb):
    return tuple(map(int, rgb))


def shuffle(iterable):
    random.shuffle(iterable)
    return iterable