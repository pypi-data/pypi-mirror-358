"""
PyWRFKit: A comprehensive Python toolkit for Weather Research and Forecasting (WRF) model data processing, analysis, and visualization.

This package provides utilities for:
- WRF coordinate handling and data manipulation
- Polar coordinate transformations for hurricane analysis
- Data downloading from meteorological sources
- Visualization and plotting utilities
- Statistical analysis and metrics
- AHPS data processing
"""

__version__ = "0.1.5"
__author__ = "Ankur Kumar"
__email__ = "ankurk017@gmail.com"

# Import core modules (always available)
from . import wrf
from . import polar
from . import download
from . import xrvar
from . import params
from . import metrics
from . import norms

# Import cartopy-dependent modules (optional)
try:
    from . import coast
    from . import plot_geog
    from . import ahps
    CARTOPY_AVAILABLE = True
except ImportError:
    CARTOPY_AVAILABLE = False
    # Create dummy modules for when cartopy is not available
    class coast:
        pass
    class plot_geog:
        pass
    class ahps:
        pass

# Define what gets imported with "from pywrfkit import *"
__all__ = [
    'wrf',
    'polar',
    'download',
    'xrvar',
    'params',
    'metrics',
    'norms',
    'coast',
    'plot_geog',
    'ahps',
    'CARTOPY_AVAILABLE'
]
