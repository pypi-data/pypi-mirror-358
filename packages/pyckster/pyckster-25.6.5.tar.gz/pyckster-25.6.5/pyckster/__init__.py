"""
Pyckster - A PyQt5-based GUI for picking seismic traveltimes and analyzing inversions
"""

# Define version and metadata in one place
__version__ = "25.6.5"
__author__ = "Sylvain Pasquet"
__email__ = "sylvain.pasquet@sorbonne-universite.fr"
__license__ = "GPLv3"

# Import and expose main functionality
from .core import main, MainWindow

# Define what's available when doing 'from pyckster import *'
__all__ = [
    'main',
    'MainWindow',
    '__version__',
]