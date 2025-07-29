# pyreliabilitypro/core/metrics.py

import numpy as np
from typing import List, Union

# What: This imports `List` and `Union` from the `typing` module.
# Why: These are used for "type hints".
# Type hints are a way to indicate the expected data types
# for function arguments and return values. They help:
# - Make code easier to understand:
#   You can immediately see what kind of data a function expects.
# - Catch errors early: Tools like MyPy (which we'll use later)
#   can check your code for type consistency before you even run it.
# - Improve autocompletion in IDEs like VS Code.
# How:
# - `List`: Indicates that an argument or
#    return value should be a Python list.
# - `Union`: Indicates that an argument or
#   return value can be one of several types.
# For example, `Union[int, float]` means it can be an integer OR a float.
from scipy.special import gamma as gamma_function


def calculate_mttf_exponential(failure_times: List[Union[int, float]]) -> float:
    # `def`: Keyword to define a function.
    # `calculate_mttf_exponential`:
    # The name of our function. It should be descriptive.
    # `(` ... `)`: Parentheses enclose the function's parameters (inputs).
    # `failure_times: List[Union[int, float]]`:
    # This is our first parameter.
    # - `failure_times`: The name of the parameter.
    # - `: List[Union[int, float]]`: The type hint.
    # It says `failure_times` is expected to be a
    # `List` where each element in the list can be
    # either an `int` (integer) or a `float` (decimal number).
    # `-> float`: This is the type hint for the return value.
    # It indicates that this function is
    # expected to return a `float` (a decimal number).

    """
    Calculates the Mean Time To Failure (MTTF)
    assuming an exponential distribution.

    For an exponential distribution, the MTTF
    is the sum of the failure times
    divided by the number of failures. (This is actually the
    definition of the sample mean,
    which is the Maximum Likelihood Estimator for the MTTF
      of an exponential distribution).

    Args:
        failure_times: A list of failure times (non-negative numbers).
                       Can be integers or floats.

    Returns:
        The calculated MTTF as a float.

    Raises:
        ValueError: If failure_times is empty or
        contains negative values.
        TypeError: If failure_times is not a list
        or contains non-numeric values.
    """
    if not isinstance(failure_times, list):
        raise TypeError("Input 'failure_times' must be a list.")

    if not failure_times:
        raise ValueError("Input 'failure_times' cannot be empty.")
    for time in failure_times:
        if not isinstance(time, (int, float)):
            # Here, we check if `time` (each individual element)
            #  is NOT an integer OR a float.
            # `(int, float)` is a tuple of types. `isinstance`
            # can check against a tuple of types.
            raise TypeError(
                f"All elements in 'failure_times' must be numbers. Found: {time} of type {type(time).__name__}"
            )
        if time < 0:
            raise ValueError(f"Failure times must be non-negative. Found: {time}")

    # --- Calculation ---
    ft_array = np.array(failure_times)
    if ft_array.size == 0:
        raise ValueError(
            "Input 'failure_times' resulted in an empty array for calculation (should be caught by list empty check)."
        )
    mttf = np.sum(ft_array) / len(ft_array)
    return float(mttf)


# ... calculate_mttf_exponential function ...
def weibull_mttf(beta: float, eta: float, gamma_loc: float = 0.0) -> float:
    """
    Calculates the Mean Time To Failure (MTTF)
    for a Weibull distribution
    given its parameters.

    The formula for Weibull MTTF is: γ + η * Γ(1 + 1/β)
    where:
    - β (beta) is the shape parameter.
    - η (eta) is the scale parameter (characteristic life).
    - γ (gamma_loc) is the location parameter
    (failure-free life or threshold).
    - Γ() is the Gamma function.

    Args:
        beta: The shape parameter (β > 0).
        eta: The scale parameter (η > 0).
        gamma_loc: The location parameter (γ),
        representing a failure-free
        operating period. Defaults to 0 for a 2-parameter Weibull.
        Note: Renamed to 'gamma_loc' to avoid conflict with the
        imported 'gamma_function'.

    Returns:
        The calculated Mean Time To Failure (MTTF) as a float.

    Raises:
        ValueError: If beta <= 0 or eta <= 0.
    """
    # --- Input Validations ---
    # Shape and scale parameters must be positive
    if beta <= 0:
        raise ValueError("Shape parameter beta (β) must be greater than 0.")
    if eta <= 0:
        raise ValueError("Scale parameter eta (η) must be greater than 0.")

    # --- Calculation ---
    # Γ(1 + 1/β) part
    try:
        gamma_term = gamma_function(1.0 + (1.0 / beta))
    except Exception as e:
        # This might happen for extremely small beta values
        # leading to overflow in 1/beta,
        # or other numerical issues with the gamma function
        # for certain inputs,
        # though rare for valid beta.
        raise ValueError(
            f"Could not compute Gamma function term for beta={beta}. Error: {e}"
        )

    mttf = gamma_loc + eta * gamma_term
    return float(mttf)  # Ensure standard Python float output
