"""
SpotInfer - A simple Python package for inference tasks.
"""

__version__ = "0.1.0"

from .main import cli
from .prepare.offers import OffersService, list_offers

__all__ = ["cli", "__version__", "OffersService", "list_offers"]
