def align_right(segments):
    """
    :param segments: length of each line
       ---
     -----
      ----
         -
        --

     :return The distance from where each segment was located
    """
    biggest = max(segments)
    for i in segments:
        if i < biggest:
            padding = (biggest - i)
        else:
            padding = 0
        yield padding


def align_centre(segments):
    """
    :param segments: length of each line

      ---
     -----
     ----
       -
      --

    :return The distance from where each segment was located
    """
    yield from [i // 2 if i != 0 else i for i in align_right(segments)]


class RangeError(Exception):
    pass


def padded(spacing: int, segments):
    """
    :param spacing: length of gaps
    :param segments: length of each line


    spacing = 1
    segments = (3, 5, 4, 1, 2)
    --- ----- ---- - --

    :return: The position of where each segment is located
    """
    pos = 0
    for line in segments:
        yield pos
        pos += line
        pos += spacing


def padded_maximum(distance: int, spacing: int, line: int):
    incr = spacing + line
    pos = 0
    while distance > pos:
        yield pos
        pos += incr


def fill_in_line(distance: int, segments):
    """
    :param distance: length of line to fill in
    :param segments: length of each line

    distance = 20
    segments = (3, 5, 4, 1, 2)
    --- ----- ---- - --

    :return: The position of where each segment is located
    """
    if sum(segments) > distance:
        raise RangeError

    spacing = distance - sum(segments)

    if len(segments) == 1:
        yield distance // 2
        return

    padding = divmod(spacing, len(segments) - 1)

    halfway = distance / 2
    for i in padded(padding[0], segments):
        if i >= halfway:
            i += padding[1]
        yield i


def find_fill_in(distance: int, lines: int):
    """
    :param distance: length of line to fill in
    :param line: The amount of lines to contain within distance

    distance = 20
    line = 8
    --------- --------- --

    :return: The position of where each segment is located, the length of the segment
    """
    if distance - lines < 0:
        raise RangeError

    if lines == 1:
        yield 0, distance
        return

    line_length, rm = divmod(distance, lines)
    segments = [line_length for _ in range(lines)]
    for x in range(rm):
        segments[x] += 1

    yield from zip(fill_in_line(distance, segments), segments)


def fill_in_shortcut(distance: int, line: int, amount: int):
    segments = [line] * amount
    return fill_in_line(distance, segments)
