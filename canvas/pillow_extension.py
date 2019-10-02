from .canvas import Canvas
from PIL import Image

class PILCanvas(Canvas):
    @classmethod
    def from_PIL(cls, im: Image):
        return cls(im.getdata(), im.size)

    @classmethod
    def from_image(cls, fp, mode):
        return cls.from_PIL(Image.open(fp).convert(mode))

    def as_PIL(self):
        im = Image.new('RGB', self.size, 'black')
        im.putdata(self.data)
        return im

    def save(self, fp, format=None, **params):
        self.as_PIL().save(fp, format=None, **params)