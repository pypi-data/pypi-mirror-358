"""
PyWRFKit: A comprehensive Python toolkit for Weather Research and Forecasting (WRF) model data processing, analysis, and visualization.

This package provides utilities for:
- WRF coordinate handling and data manipulation
- Geographic data processing (LULC, NDVI)
- Polar coordinate transformations for hurricane analysis
- Data downloading from meteorological sources
- Visualization and plotting utilities
- Statistical analysis and metrics
- AHPS data processing
"""

__version__ = "0.1.0"
__author__ = "Ankur Kumar"
__email__ = "ankurk017@gmail.com"

# Import all modules for easy access
from . import wrf
from . import geog
from . import polar
from . import download
from . import coast
from . import plot_geog
from . import ahps
from . import xrvar
from . import params
from . import metrics
from . import norms

# Define what gets imported with "from pywrfkit import *"
__all__ = [
    'wrf',
    'geog', 
    'polar',
    'download',
    'coast',
    'plot_geog',
    'ahps',
    'xrvar',
    'params',
    'metrics',
    'norms'
]
