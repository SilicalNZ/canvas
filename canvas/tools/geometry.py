class ThreeDimensional:
    @staticmethod
    def linear(point0, point1, itr: int=0):
        """Returns all the valid pixel coordinates between 2 points on a 3d-axis
        """
        x0, y0, z0 = point0
        x1, y1, z1 = point1

        if point0 == point1:
            return [point0]
        link = []

        width, height, depth = x1 - x0, y1 - y0, z1 - z0

        def direction(a: int):
            # determines if pixel needs to be moved, and in what direction
            return -1 if a < 0 else 1 if a > 0 else 0

        w, h, d = direction(width), direction(height), direction(depth)

        # Create lists of all valid pixels, of each linear planes
        widths = tuple(range(x0, x1 + w, w)) if w != 0 else [x0]
        heights = tuple(range(y0, y1 + h, h)) if h != 0 else [y0]
        depths = tuple(range(z0, z1 + d, d)) if d != 0 else [z0]
        xyz = (widths, heights, depths)

        # Return no changes, as there are no changes to be made
        if all(1 == len(i) for i in xyz):
            link.append((x0, y0, z0))
            return

        if itr >= 1:
            steps = min(len(max(xyz, key=len)), itr)
        else:
            steps = len(max(xyz, key=len))
        literal_steps = steps - 1

        # Creates a literal len() of each list, for faster comprehension
        xyz = tuple((i, len(i) - 1) for i in xyz)

        for i in range(0, steps):
            progress = i / literal_steps
            x = widths[int(progress * xyz[0][1] + 0.5)]
            y = heights[int(progress * xyz[1][1] + 0.5)]
            z = depths[int(progress * xyz[2][1] + 0.5)]

            link.append((x, y, z))
        return link


class TwoDimensional:
    @staticmethod
    def linear(point0, point1, itr: int=0):
        """Returns all the valid pixel coordinates between 2 points on a 2d-axis
        """
        x0, y0 = point0
        x1, y1 = point1
        if point0 == point1:
            return [point0]
        link = []

        width, height = x1 - x0, y1 - y0

        def direction(a: int):
            # determines if pixel needs to be moved, and in what direction
            return -1 if a < 0 else 1 if a > 0 else 0

        w, h = direction(width), direction(height)

        # Create lists of all valid pixels, of each linear planes
        widths = tuple(range(x0, x1 + w, w)) if w != 0 else [x0]
        heights = tuple(range(y0, y1 + h, h)) if h != 0 else [y0]
        xyz = (widths, heights)

        # Return no changes, as there are no changes to be made
        if all(1 == len(i) for i in xyz):
            link.append((x0, y0))
            return link

        steps = len(max(xyz, key=len)) if itr <= 1 else itr
        literal_steps = steps - 1

        # Creates a literal len() of each list, for faster comprehension
        xyz = tuple((i, len(i) - 1) for i in xyz)

        for i in range(0, steps):
            progress = i / literal_steps
            x = widths[int(progress * xyz[0][1] + 0.5)]
            y = heights[int(progress * xyz[1][1] + 0.5)]

            link.append((x, y))
        return link

    @staticmethod
    def point_bounce(point0, point1, boundary=256):
        x0, y0 = point0
        x1, y1 = point1

        x_dist, y_dist = x0 - x1, y0 - y1
        if abs(x_dist) >= abs(y_dist):
            y = 0 if abs(y_dist) < boundary // 2 else boundary - 1
            x = x0 - x_dist // 2
        else:
            x = 0 if abs(x_dist) < boundary // 2 else boundary - 1
            y = y0 - y_dist // 2

        line1 = TwoDimensionalLink.linear((x0, y0), (x, y))
        line2 = TwoDimensionalLink.linear((x0, y0), (x, y))

        link = line1 + line2[1:]
        return link

    @staticmethod
    def circle_from_point(point0, radius: int=0):
        x0, y0 = point0
        r = radius

        x, y = r, 0
        dx, dy = 1, 1
        err = dx - r << 1

        link = set()

        while x >= y:
            link.update((
                (x0 + x, y0 + y),
                (x0 + y, y0 + x),
                (x0 - y, y0 + x),
                (x0 - x, y0 + y),
                (x0 - x, y0 - y),
                (x0 - y, y0 - x),
                (x0 + y, y0 - x),
                (x0 + x, y0 - y)
            ))

            if err <= 0:
                y += 1
                err += dy
                dy += 2
            if err > 0:
                x -= 1
                dx += 2
                err += dx - r << 1
        return list(link)  # Unsorted due to complexity
