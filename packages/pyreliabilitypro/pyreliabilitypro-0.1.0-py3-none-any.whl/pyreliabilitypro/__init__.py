# pyreliabilitypro/__init__.py

"""
PyReliabilityPro: A Python toolkit for reliability analysis.

This package provides tools for analyzing failure data using common reliability
engineering distributions and metrics.
"""

# Import key functions from submodules to make them easily accessible
# at the top-level of the package, e.g., `pyreliabilitypro.weibull_pdf()`
from .core.distributions import (
    weibull_pdf,
    weibull_cdf,
    weibull_sf,
    weibull_hf,
    weibull_fit,
)

from .core.metrics import (
    calculate_mttf_exponential,
    weibull_mttf,
)

# Define the package version. This is a standard practice.
__version__ = "0.1.0"

# __all__ defines the public API of the package when a user does
# `from pyreliabilitypro import *`. It's good practice to be explicit.
__all__ = [
    # Functions from distributions module
    "weibull_pdf",
    "weibull_cdf",
    "weibull_sf",
    "weibull_hf",
    "weibull_fit",
    # Functions from metrics module
    "calculate_mttf_exponential",
    "weibull_mttf",
    # Package version
    "__version__",
]
