"""PyConfBox Django Integration Plugin.

This plugin provides Django integration for PyConfBox, allowing you to use
PyConfBox configurations seamlessly within Django applications.
"""

__version__ = "0.1.0"
__author__ = "Gabriel Ki"
__email__ = "edc1901@gmail.com"

from .middleware import PyConfBoxMiddleware
from .settings import DjangoStorage

__all__ = ["PyConfBoxMiddleware", "DjangoStorage"]
