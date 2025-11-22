"""
ARTFIMA (Autoregressive Tempered Fractionally Integrated Moving Average) 
Python Implementation

This package provides a comprehensive Python implementation of the ARTFIMA model
based on the R artfima package source code.
"""

from .artfima import artfima, ARTFIMAResult
from .tacvf import artfimaTACVF
from .sdf import artfimaSDF, periodogram
from .utils import ARToPacf, PacfToAR, InvertibleQ

__version__ = "1.0.0"
__all__ = [
    "artfima",
    "ARTFIMAResult",
    "artfimaTACVF",
    "artfimaSDF",
    "periodogram",
    "ARToPacf",
    "PacfToAR",
    "InvertibleQ",
]

