# brinias/__init__.py

from .core import Brinias
from .api import train_model, make_prediction

__version__ = "0.1.0"
__all__ = ["Brinias", "train_model", "make_prediction"]