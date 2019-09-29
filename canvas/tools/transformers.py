from ..canvas import Canvas

def rotate(canvas: Canvas, rotations: int=1):
    width = canvas.width
    data = list(canvas)

    for _ in range(rotations):
        data = [canvas[i::canvas.width] for i in range(canvas.width)]

    return data
