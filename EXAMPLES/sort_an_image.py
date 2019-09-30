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
    c.rearrange(canvas.tools.yiq) # Sorts by luminosity
    return c

@open_and_save_image
def rearrange_segments(c: canvas.Canvas):
    controller = canvas.CanvasController(c)
    # A rectangle of width = default, length = 20
    width, length = c.width, c.length // 20
    # Splits the canvas into those rectangles
    # and returns a generator to iterate through
    for i in controller.fragment((width, length)):
        # Sort each rectangle by luminosity
        i.rearrange(canvas.tools.yiq)
    # Save all changes
    controller.unscope_all()
    return c
