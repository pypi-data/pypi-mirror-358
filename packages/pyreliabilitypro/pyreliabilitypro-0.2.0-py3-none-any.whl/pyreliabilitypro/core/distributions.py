# pyreliabilitypro/core/distributions.py
import numpy as np
import scipy.stats as stats
from typing import Union
from typing import List, Tuple, Optional


def weibull_pdf(
    x: Union[float, np.ndarray], beta: float, eta: float, gamma: float = 0.0
) -> Union[float, np.ndarray]:
    """
    Calculates the Probability Density Function (PDF) for the 2-parameter or
    3-parameter Weibull distribution.

    The 3-parameter Weibull distribution has:
    - beta (β): Shape parameter (k in scipy)
    - eta (η): Scale parameter (λ in some texts, 'scale' in scipy)
    - gamma (γ): Location parameter (loc in scipy), threshold, or failure-free life.
                 Defaults to 0 for a 2-parameter Weibull.

    Args:
        x: The value(s) at which to evaluate the PDF.
        Can be a single float or a NumPy array.
        beta: The shape parameter (β > 0). Also known as k.
        eta: The scale parameter (η > 0). Also known as lambda (λ).
        gamma: The location parameter (γ). Defaults to 0 for a 2-parameter Weibull.
               Represents a failure-free operating period. x must be >= gamma.

    Returns:
        The PDF value(s) corresponding to x. Returns a float if x is a float,
        or a NumPy array if x is a NumPy array.

    Raises:
        ValueError: If beta <= 0, eta <= 0, or if any x < gamma.
    """
    if beta <= 0:
        raise ValueError("Shape parameter beta (β) must be greater than 0.")
        # Shape parameter β must be positive for
        # the Weibull distribution to be well-defined.

    if eta <= 0:
        raise ValueError("Scale parameter eta (η) must be greater than 0.")
        # Scale parameter η must also be positive.

    x_arr = np.asarray(x)
    if np.any(x_arr < gamma):
        raise ValueError(
            f"All values of x must be greater than or equal to the location parameter gamma (γ={gamma}). Found x < gamma."
        )

    # --- Calculation using SciPy's Weibull_min distribution ---
    # This section explains the mapping from our chosen parameter names to SciPy's.
    # SciPy's `weibull_min` distribution maps parameters as follows:
    # - Its shape parameter `c` corresponds to our `beta` (β).
    # - Its location parameter `loc` corresponds to our `gamma` (γ).
    # - Its scale parameter `scale` corresponds to our `eta` (η).
    # It's vital to get this mapping correct when calling the SciPy function.

    pdf_values = stats.weibull_min.pdf(x_arr, c=beta, loc=gamma, scale=eta)
    # This is the core calculation.
    # `stats.weibull_min`: Accesses the Weibull distribution
    # object within SciPy's stats module.
    # (The `_min` refers to it being for smallest extreme values, which is
    # the standard Weibull for lifetime analysis).
    # `.pdf(...)`: Calls the Probability Density Function
    # method of this distribution.
    # Arguments to `stats.weibull_min.pdf()`:
    # `x_arr`: The (NumPy array of) values at which to calculate the PDF.
    # `c=beta`: Passes our `beta` (shape) as SciPy's shape parameter `c`.
    # `loc=gamma`: Passes our `gamma` (location) as SciPy's location parameter `loc`.
    #              SciPy internally handles the `(x - gamma)` shift.
    #   `scale=eta`: Passes our `eta` (scale) as SciPy's scale parameter `scale`.
    # The result, `pdf_values`, will be a NumPy array
    # containing the PDF value for each
    # element in `x_arr`. If `x_arr` was a
    # 0-dimensional array (from a scalar `x`), then
    # `pdf_values` will also be a 0-dimensional array.
    # Why: If the user passed in a single number for `x`,
    # they likely expect a single number back,
    # not a 0-dimensional NumPy array.
    # This makes the function more user-friendly.
    if isinstance(x, (int, float)):
        return float(pdf_values.item())
    else:
        return pdf_values


def weibull_cdf(
    x: Union[float, np.ndarray], beta: float, eta: float, gamma: float = 0.0
) -> Union[float, np.ndarray]:
    """
    Calculates the Cumulative Distribution Function (CDF)
    for the 2-parameter or
    3-parameter Weibull distribution.

    The CDF, F(x) = P(T <= x), gives the probability that a failure will occur
    by time x.

    The 3-parameter Weibull distribution has:
    - beta (β): Shape parameter (k in scipy)
    - eta (η): Scale parameter (λ in some texts, 'scale' in scipy)
    - gamma (γ): Location parameter (loc in scipy), threshold,
    or failure-free life.
                 Defaults to 0 for a 2-parameter Weibull.

    Args:
        x: The time(s) at which to evaluate the CDF.
        Can be a single float or a NumPy array.
           Values less than gamma will have a CDF of 0.
        beta: The shape parameter (β > 0). Also known as k.
        eta: The scale parameter (η > 0). Also known as lambda (λ).
        gamma: The location parameter (γ).
        Defaults to 0 for a 2-parameter Weibull.

    Returns:
        The CDF value(s) corresponding to x.
          A probability between 0 and 1.
        Returns a float if x is a float,
        or a NumPy array if x is a NumPy array.

    Raises:
        ValueError: If beta <= 0 or eta <= 0.
    """
    # --- Input Validations ---
    # Shape and scale parameters must be positive
    if beta <= 0:
        raise ValueError("Shape parameter beta (β) must be greater than 0.")
    if eta <= 0:
        raise ValueError("Scale parameter eta (η) must be greater than 0.")

    # Convert x to a numpy array for consistent handling.
    # We don't need to raise an error
    # if x < gamma here, because the CDF is well-defined
    # as 0 for x < gamma. SciPy's cdf
    # function handles this correctly when loc=gamma.
    x_arr = np.asarray(x)

    # --- Calculation using SciPy's Weibull_min distribution ---
    # Parameter mapping is the same as for PDF:
    # - Our beta (β) -> SciPy's shape 'c'
    # - Our eta (η)  -> SciPy's scale 'scale'
    # - Our gamma (γ) -> SciPy's location 'loc'

    # SciPy's cdf function correctly returns 0 for x < loc (gamma)
    # and 1 for x -> infinity.
    cdf_values = stats.weibull_min.cdf(x_arr, c=beta, loc=gamma, scale=eta)

    # Ensure correct return type (scalar float or NumPy array)
    # based on original input x
    if isinstance(x, (int, float)):
        return float(cdf_values.item())  # .item() extracts scalar from 0-d array
    else:
        return cdf_values


def weibull_sf(
    x: Union[float, np.ndarray], beta: float, eta: float, gamma: float = 0.0
) -> Union[float, np.ndarray]:
    """
    Calculates the Survival Function (SF),
    also known as the Reliability Function R(x),
    for the 2-parameter or 3-parameter Weibull distribution.

    The Survival Function, S(x) = P(T > x),
    gives the probability that an item
    will survive beyond time x. It is equivalent to 1 - CDF(x).

    The 3-parameter Weibull distribution has:
    - beta (β): Shape parameter (k in scipy)
    - eta (η): Scale parameter (λ in some texts, 'scale' in scipy)
    - gamma (γ): Location parameter (loc in scipy),
      threshold, or failure-free life.
      Defaults to 0 for a 2-parameter Weibull.

    Args:
        x: The time(s) at which to evaluate the Survival Function.
           Can be a single float or a NumPy array.
           Values less than gamma will have an SF of 1.0.
        beta: The shape parameter (β > 0). Also known as k.
        eta: The scale parameter (η > 0). Also known as lambda (λ).
        gamma: The location parameter (γ). Defaults to 0 for a 2-parameter Weibull.

    Returns:
        The Survival Function value(s) corresponding to x.
        A probability between 0 and 1.
        Returns a float if x is a float, or a NumPy array if x is a NumPy array.

    Raises:
        ValueError: If beta <= 0 or eta <= 0.
    """
    # --- Input Validations ---
    # Shape and scale parameters must be positive
    if beta <= 0:
        raise ValueError("Shape parameter beta (β) must be greater than 0.")
    if eta <= 0:
        raise ValueError("Scale parameter eta (η) must be greater than 0.")

    # Convert x to a numpy array for consistent handling.
    # SciPy's sf function handles x < gamma correctly (returning 1.0).
    x_arr = np.asarray(x)

    # --- Calculation using SciPy's Weibull_min distribution ---
    # Parameter mapping is the same as for PDF and CDF:
    # - Our beta (β) -> SciPy's shape 'c'
    # - Our eta (η)  -> SciPy's scale 'scale'
    # - Our gamma (γ) -> SciPy's location 'loc'

    # SciPy's sf (Survival Function) method.
    # It correctly returns 1.0 for x < loc (gamma)
    # and approaches 0 for x -> infinity.
    sf_values = stats.weibull_min.sf(x_arr, c=beta, loc=gamma, scale=eta)

    # Ensure correct return type (scalar float or NumPy array)
    #  based on original input x
    if isinstance(x, (int, float)):
        return float(sf_values.item())  # .item() extracts scalar from 0-d array
    else:
        return sf_values


def weibull_hf(
    x: Union[float, np.ndarray], beta: float, eta: float, gamma: float = 0.0
) -> Union[float, np.ndarray]:
    """
    Calculates the Hazard Function (HF),
    also known as the instantaneous failure rate h(x) or λ(x),
    for the 2-parameter or 3-parameter Weibull distribution
    using its direct mathematical formula.

    The Hazard Function, h(x), for Weibull is:
    - 0                      if x < gamma
    - (β/η) * ((x-γ)/η)^(β-1) if x >= gamma
    (with special handling for x=gamma)
      - If x = gamma and β < 1, h(x) -> infinity.
      - If x = gamma and β = 1, h(x) = 1/η.
      - If x = gamma and β > 1, h(x) = 0.

    Args:
        x: The time(s) at which to evaluate the Hazard Function.
           Can be a single float or a NumPy array.
        beta: The shape parameter (β > 0).
        eta: The scale parameter (η > 0).
        gamma: The location parameter (γ).
        Defaults to 0 for a 2-parameter Weibull.

    Returns:
        The Hazard Function value(s) corresponding to x. This is a rate.
        Returns a float if x is a float, or a NumPy array if x is a NumPy array.
        Can return np.inf for the case x=gamma and beta < 1.

    Raises:
        ValueError: If beta <= 0 or eta <= 0.
    """
    # --- Input Validations ---
    if not isinstance(beta, (int, float)) or beta <= 0:  # Added type check for beta
        raise ValueError("Shape parameter beta (β) must be a positive number.")
    if not isinstance(eta, (int, float)) or eta <= 0:  # Added type check for eta
        raise ValueError("Scale parameter eta (η) must be a positive number.")
    if not isinstance(gamma, (int, float)):  # Added type check for gamma
        raise ValueError("Location parameter gamma (γ) must be a number.")
    # No type check for x here as np.asarray will
    # handle list/scalar/array and convert later.

    # Convert x to a numpy array of floats for consistent calculations
    try:
        x_arr = np.asarray(x, dtype=float)
        if x_arr.ndim == 0 and isinstance(
            x, (list, tuple)
        ):  # Handles case np.asarray([single_list_val])
            x_arr = np.array([float(i) for i in x], dtype=float)
        elif x_arr.ndim > 1:
            raise ValueError("'x' must be a scalar or 1-dimensional array-like.")
    except (TypeError, ValueError) as e:
        raise TypeError(
            f"Input 'x' must be a scalar or an array-like object of numbers. Error: {e}"
        )

    # Initialize hazard_values as a NumPy array of floats,
    # with the same shape as x_arr
    # This is important if x_arr is scalar (0-d array),
    # result should also be scalar later.
    hazard_values = np.zeros_like(x_arr, dtype=float)

    # --- Calculations based on x relative to gamma ---

    # Part 1: x < gamma
    # For these values, the hazard rate is 0.
    # The initialization to np.zeros_like already handles this,
    # but we can be explicit if preferred for clarity.
    mask_below_gamma = x_arr < gamma
    hazard_values[mask_below_gamma] = 0.0

    # Part 2: x = gamma
    mask_at_gamma = x_arr == gamma
    if np.any(mask_at_gamma):  # Check if any x is exactly gamma
        if beta < 1.0:
            hazard_values[mask_at_gamma] = np.inf
        elif beta == 1.0:
            hazard_values[mask_at_gamma] = 1.0 / eta
        else:  # beta > 1.0
            hazard_values[mask_at_gamma] = 0.0

    # Part 3: x > gamma
    mask_above_gamma = x_arr > gamma
    if np.any(mask_above_gamma):  # Check if any x is greater than gamma
        # Operate only on the relevant slice of x_arr
        #  to avoid issues with x <= gamma
        x_slice_above_gamma = x_arr[mask_above_gamma]

        shifted_x = x_slice_above_gamma - gamma
        term1 = beta / eta
        term2_base = shifted_x / eta

        # term2_base here will always be > 0
        # because x_slice_above_gamma > gamma and eta > 0.
        # So, no issues with 0 to a negative power for this part.
        term2_powered = np.power(term2_base, beta - 1.0)

        hazard_values[mask_above_gamma] = term1 * term2_powered

    if isinstance(x, (int, float)):
        # x_arr would have been a 0-d array, so hazard_values is also 0-d.
        # .item() extracts the single scalar value.
        return float(hazard_values.item())
    else:
        return hazard_values


# pyreliabilitypro/core/distributions.py
# (other functions and imports are here)

# pyreliabilitypro/core/distributions.py
# (other functions and imports are here)


def weibull_fit(
    failure_times: Union[List[Union[int, float]], np.ndarray],
    fit_gamma: bool = False,
    initial_beta: Optional[float] = None,
) -> Tuple[float, float, float]:
    """
    Estimates the parameters (beta, eta, and optionally gamma) of a Weibull
    distribution from a list of failure times using Maximum Likelihood Estimation (MLE)
    via scipy.stats.weibull_min.fit().

    Our toolkit standard parameter order is (beta, eta, gamma).
    SciPy's weibull_min parameters are (shape 'c', location 'loc', scale 'scale').
    Mapping:
        Our beta (shape) -> SciPy's 'c'
        Our eta (scale)  -> SciPy's 'scale'
        Our gamma (loc)  -> SciPy's 'loc'

    Args:
        failure_times: A list or NumPy array of failure times.
        fit_gamma: If True, attempts to fit the 3-parameter Weibull (beta, eta, gamma).
                   If False (default), fits a 2-parameter Weibull, fixing gamma (loc) to 0.0.
        initial_beta: Optional initial guess for the shape parameter (beta -> SciPy 'c').
                      Providing other initial guesses is not supported in this simplified wrapper.

    Returns:
        A tuple containing the estimated parameters in the order: (beta, eta, gamma).
        If fit_gamma is False, the returned gamma will be 0.0.

    Raises:
        ValueError: If data is invalid or fitting fails to converge.
        TypeError: If data type is incorrect.
    """
    # --- Input Validations ---
    if not isinstance(failure_times, (list, np.ndarray)):
        raise TypeError("Input 'failure_times' must be a list or NumPy array.")
    data = np.asarray(failure_times, dtype=float)
    if data.ndim != 1:
        raise ValueError("'failure_times' must be a 1-dimensional array or list.")
    if data.size < 2:
        raise ValueError("At least two data points are required to fit a distribution.")
    if np.any(np.isnan(data)) or np.any(np.isinf(data)):
        raise ValueError("Input 'failure_times' must not contain NaN or Inf values.")
    if not fit_gamma and np.any(data <= 0):
        raise ValueError(
            "Failure times must be strictly positive for a 2-parameter Weibull fit (gamma fixed at 0)."
        )

    try:
        if fit_gamma:
            # Fit 3 parameters. Call is different if we have an initial guess for shape.
            if initial_beta is not None:
                # The first positional argument after 'data' is the initial guess for the first shape param (c).
                c, loc, scale = stats.weibull_min.fit(data, initial_beta)
            else:
                c, loc, scale = stats.weibull_min.fit(data)

            estimated_beta = c
            estimated_eta = scale
            estimated_gamma = loc
        else:
            # Fit 2 parameters, fixing location (gamma) to 0.
            if initial_beta is not None:
                # The first positional argument after 'data' is the initial guess for shape (c).
                # `floc=0.0` is a keyword argument that fixes location.
                c, loc, scale = stats.weibull_min.fit(data, initial_beta, floc=0.0)
            else:
                c, loc, scale = stats.weibull_min.fit(data, floc=0.0)

            estimated_beta = c
            estimated_eta = scale
            estimated_gamma = 0.0  # We know this was fixed, so loc returned should be 0, but we set it explicitly.

    except RuntimeError as e:
        raise ValueError(
            f"Weibull fitting failed to converge. Error: {e}. Try checking data or providing an initial beta guess."
        ) from e
    except Exception as e:
        raise ValueError(
            f"An unexpected error occurred during Weibull fitting: {e}"
        ) from e

    # Return in our standard order: beta, eta, gamma
    return float(estimated_beta), float(estimated_eta), float(estimated_gamma)
