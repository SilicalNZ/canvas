class LineBalancer:
    def __init__(self, lines):
        self.lines = tuple(lines)

    @property
    def total_distance(self):
        return sum(self.lines)

    @property
    def _minimal_distance(self):
        return self.total_distance - self.lines[-1]

    def padded(self, distance: int):
        pos = 0
        for line in self.lines:
            yield pos
            pos += line
            pos += distance

    def fill_in(self, distance: int):
        if self.total_distance > distance:
            raise AssertionError()

        spacing = distance - self.total_distance
        padding = divmod(spacing, len(self.lines) - 1)

        halfway = distance / 2
        for i in self.padded(padding[0]):
            if i >= halfway:
                i += padding[1]
            yield i

    def align_right(self):
        """
        3   ---
        5 -----
        4  ----
        1     -
        2    --
        :return The new alignment distance from the old alignment
        """
        biggest = max(self.lines)
        for i in self.lines:
            if i < biggest:
                padding = (biggest - i)
            else:
                padding = 0
            yield padding

    def align_centre(self):
        """
        3  ---
        5 -----
        4 ----
        1   -
        2  --
        :return The new alignment distance from the old alignment
        """
        yield from [i // 2 if i != 0 else i for i in self.align_right()]


if __name__ == '__main__':
    this = LineBalancer((2, 2, 2, 2))
    [print(i) for i in this.padded(3)]
