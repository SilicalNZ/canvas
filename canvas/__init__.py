try:
    from PIL import Image
except ImportError:
    import warnings
    warnings.warn('Pillow failed to import. PIL-specific functionality will be unavailable.')
    from .canvas import Canvas
else:
    from .pillow_extension import PILCanvas as Canvas

from .canvas import SimpleCanvasAbstraction as CanvasApplier
from .canvas import CanvasController
from .canvas import CanvasMerger
from . import tools