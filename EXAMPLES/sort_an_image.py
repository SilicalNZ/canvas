import canvas

from PIL import Image


def open_and_save_image(func):
    def wrapper():
        im = Image.open('test_image.png')
        c = canvas.Canvas(im.getdata(), im.size)

        c = func(c)

        im.putdata(c.getdata())
        im.save('result_image.png')
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
