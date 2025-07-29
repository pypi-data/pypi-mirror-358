# pyreliabilitypro/core/__init__.py

"""
The core module of PyReliabilityPro, providing fundamental reliability
calculations for distributions and metrics.
"""

# This file makes 'core' a Python sub-package.
# We can also re-export from here if we wanted users to do:
# `from pyreliabilitypro.core import weibull_pdf`
# This mirrors the logic in the top-level __init__.py for consistency.

from .distributions import (
    weibull_pdf,
    weibull_cdf,
    weibull_sf,
    weibull_hf,
    weibull_fit,
)

from .metrics import (
    calculate_mttf_exponential,
    weibull_mttf,
)


__all__ = [
    "weibull_pdf",
    "weibull_cdf",
    "weibull_sf",
    "weibull_hf",
    "weibull_fit",
    "calculate_mttf_exponential",
    "weibull_mttf",
]
