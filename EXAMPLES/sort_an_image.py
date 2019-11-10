from canvas import *


def open_and_save_image(func_or_images):
    if callable(func_or_images):
        return open_and_save_image(('test_image.png', ))(func_or_images)
    def caller(func):
        def wrapper():
            c = tuple(Canvas.from_image(image, 'RGB') for image in func_or_images)
            c = func(*c)
            c.save('result_image.png', 'RGB')
        return wrapper
    return caller


@open_and_save_image
def rearrange(c: Canvas):
    # Sorts by luminosity
    c.rearrange(tools.yiq)
    return c


@open_and_save_image
def rearrange_segments(c: Canvas):
    splitter = Splitter(c)
    # A rectangle of width = default, length = 20
    width, length = c.width, c.length // 20
    # Splits the canvas into quadrilaterals
    # and returns a generator to iterate through
    for i in splitter.fragment((width, length)):
        # Sort each rectangle by luminosity
        i.rearrange(tools.yiq)
    # Save all changes
    splitter.unscope_all()
    return c


@open_and_save_image
def rearrange_shape(c: Canvas):
    layer = Layer(c)
    # Assigns the area of the circle
    layer.intersection(tools.circle)
    # Assings the area of the triangle
    # that is within the circles area
    layer.intersection(tools.triangle)
    # Sort each rectangle by luminosity
    layer.rearrange(tools.yiq)
    # Save all changes
    layer.unscope()
    return c


@open_and_save_image
def rearrange_tessellation(c: Canvas):
    splitter = Splitter(c)
    # How big the shapes should be
    size = (40, 40)
    # Splits the canvas into quadrilaterals
    # and returns a generator to iterate through
    for i in splitter.fragment(size):
        # Flips the canvas
        i.reverse()
        # Make a triangle and sort it
        layer = Layer(i)
        layer.intersection(tools.triangle)
        layer.rearrange(tools.yiq)
        layer.unscope()
        # Unflips the canvas
        i.reverse()
    # Save current changes
    splitter.unscope_all()

    # Create an unaligned canvas, so that the next iteration
    # is halfway between the old iteration
    portion = splitter.portion((-20, 0, *splitter.size))
    new_splitter = Splitter(portion)

    for i in new_splitter.fragment(size):
        # Make a triangle and sort it
        layer = Layer(i)
        layer.shape_and_rearrange(tools.triangle, tools.yiq)
        layer.unscope()
    # Save up the chain
    new_splitter.unscope_all()
    splitter.unscope_all()
    return c


@open_and_save_image
def operations_within_tessellation(c: Canvas):
    splitter = Splitter(c)
    # How big the shapes should be
    size = (20, 20)
    # Splits the canvas into quadrilaterals
    # and returns a generator to iterate through
    for i in splitter.fragment(size):
        # Another splitter to do nested operations
        rectangle = Splitter(i)
        # Splits each quadrilarereal into two rectangles of same width and even length
        for x, width in enumerate(rectangle.crack(sizes_per_width=2)):
            width = Layer(width)
            # Switches between both triangle directions
            if x == 0:
                width.intersection(tools.vertical_lines, reversed, tuple, tools.triangle)
            else:
                width.intersection(tools.vertical_lines, tools.triangle)
            width.rearrange(tools.yiq)
            width.unscope()
        # Saves to splitter, so that operations aren't overwritten
        rectangle.unscope_all()
        # Splits each quadrilarereal into two rectangles of same length and even width
        for y, length in enumerate(rectangle.crack(sizes_per_length=2)):
            length = Layer(length)
            # Switches between both triangle directions
            # (This is an alternative method to rearrange_tessllation)
            if y == 0:
                length.intersection(reversed, tuple, tools.triangle)
            else:
                length.intersection(tools.triangle)
            length.rearrange(tools.yiq)
            length.unscope()
        rectangle.unscope_all()
    splitter.unscope_all()


@open_and_save_image(('sili.png', 'test_image2.png'))
def movement(*canvases):
    #Two trackers that keep an eye on the rearrange
    tracker0 = Tracker(canvases[0])
    tracker0.rearrange(tools.yiq)

    tracker1 = Tracker(canvases[1])
    tracker1.rearrange(tools.yiq)

    # Binds the trackers together, same methods as Tracker
    tracker = Binder(tracker0, tracker1)

    # The args used are canvases of transformation
    # eg: (0, 0) -> (3, 3), ... = [(0, 0), (1, 1), (2, 2), (3, 3)], ...
    constructor = Constructor(tracker,
                              Canvas.from_empty_size(tracker.size, CanvasNone),
                              tracker.movement(tools.TwoDimensional.linear),
                              tracker.transition(tools.ThreeDimensional.linear))
    return constructor.movement(0.5)
