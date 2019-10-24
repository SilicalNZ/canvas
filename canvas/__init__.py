try:
    from PIL import Image
except ImportError:
    import warnings
    warnings.warn('Pillow failed to import. PIL-specific functionality will be unavailable.')
    from .Canvas import Canvas
else:
    from .pillow_extension import PILCanvas as Canvas

from .Layer import Layer
from .Splitter import Splitter
from .Merger import Merger
from . import tools