from .canvas import Canvas
from PIL import Image

class PILCanvas(Canvas):
    @classmethod
    def from_PIL(cls, im: Image):
        return cls(im.getdata(), im.size)

    @classmethod
    def from_image(cls, fp, mode):
        return cls.from_PIL(Image.open(fp).convert(mode))

    def as_PIL(self, mode):
        im = Image.new(mode, self.size, 'black')
        im.putdata(self.data)
        return im

    def save(self, fp, mode, format=None, **params):
        self.as_PIL(mode).save(fp, format=None, **params)
