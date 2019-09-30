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
