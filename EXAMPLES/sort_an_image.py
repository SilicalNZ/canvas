import canvas


def open_and_save_image(func):
    def wrapper():
        c = canvas.Canvas.from_image('test_image.png', 'RGB')
        c = func(c)
        c.save('result_image.png', 'RGB')
    return wrapper

@open_and_save_image
def rearrange(c: canvas.Canvas):
    # Sorts by luminosity
    c.rearrange(canvas.tools.yiq)
    return c

@open_and_save_image
def rearrange_segments(c: canvas.Canvas):
    controller = canvas.CanvasController(c)
    # A rectangle of width = default, length = 20
    width, length = c.width, c.length // 20
    # Splits the canvas into quadrilaterals
    # and returns a generator to iterate through
    for i in controller.fragment((width, length)):
        # Sort each rectangle by luminosity
        i.rearrange(canvas.tools.yiq)
    # Save all changes
    controller.unscope_all()
    return c

@open_and_save_image
def rearrange_shape(c: canvas.Canvas):
    applier = canvas.CanvasApplier(c)
    # Assigns the area of the circle
    applier.intersection(canvas.tools.circle)
    # Assings the area of the triangle
    # that is within the circles area
    applier.intersection(canvas.tools.triangle)
    # Sort each rectangle by luminosity
    applier.rearrange(canvas.tools.yiq)
    # Save all changes
    applier.save()
    return c

@open_and_save_image
def rearrange_tessellation(c: canvas.Canvas):
    controller = canvas.CanvasController(c)
    # How big the shapes should be
    size = (40, 40)
    # Splits the canvas into quadrilaterals
    # and returns a generator to iterate through
    for i in controller.fragment(size):
        # Flips the canvas
        i.reverse()
        # Make a triangle and sort it
        applier = canvas.CanvasApplier(i)
        applier.intersection(canvas.tools.triangle)
        applier.rearrange(canvas.tools.yiq)
        applier.save()
        # Unflips the canvas
        i.reverse()
    # Save current changes
    controller.unscope_all()

    # Create an unaligned canvas, so that the next iteration
    # is halfway between the old iteration
    portion = controller.portion((-20, 0, *controller.size))
    new_controller = canvas.CanvasController(portion)

    for i in new_controller.fragment(size):
        # Make a triangle and sort it
        applier = canvas.CanvasApplier(i)
        applier.shape_and_rearrange(canvas.tools.triangle, canvas.tools.yiq)
        applier.save()
    # Save up the chain
    new_controller.unscope_all()
    controller.unscope_all()
    return c


@open_and_save_image
def operations_within_tessellation(c: canvas.Canvas):
    controller = canvas.CanvasController(c)
    # How big the shapes should be
    size = (20, 20)
    # Splits the canvas into quadrilaterals
    # and returns a generator to iterate through
    for i in controller.fragment(size):
        # Another controller to do nested operations
        rectangle = canvas.CanvasController(i)
        # Splits each quadrilarereal into two rectangles of same width and even length
        for x, width in enumerate(rectangle.crack(sizes_per_width=2)):
            width = canvas.CanvasApplier(width)
            # Switches between both triangle directions
            if x == 0:
                width.intersection(canvas.tools.vertical_lines, reversed, tuple, canvas.tools.triangle)
            else:
                width.intersection(canvas.tools.vertical_lines, canvas.tools.triangle)
            width.rearrange(canvas.tools.yiq)
            width.save()
        # Saves to controller, so that operations aren't overwritten
        rectangle.unscope_all()
        # Splits each quadrilarereal into two rectangles of same length and even width
        for y, length in enumerate(rectangle.crack(sizes_per_length=2)):
            length = canvas.CanvasApplier(length)
            # Switches between both triangle directions
            # (This is an alternative method to rearrange_tessllation)
            if y == 0:
                length.intersection(reversed, tuple, canvas.tools.triangle)
            else:
                length.intersection(canvas.tools.triangle)
            length.rearrange(canvas.tools.yiq)
            length.save()
        rectangle.unscope_all()
    controller.unscope_all()
    return c
