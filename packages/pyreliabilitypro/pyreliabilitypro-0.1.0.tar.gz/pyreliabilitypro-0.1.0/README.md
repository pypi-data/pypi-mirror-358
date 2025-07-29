# PyReliabilityPro: A Python Toolkit for Reliability Analysis

[![Python CI Pipeline](https://github.com/Santtosh19/PyReliabilityPro/actions/workflows/ci.yml/badge.svg)](https://github.com/Santtosh19/PyReliabilityPro/actions/workflows/ci.yml) 
[![codecov](https://codecov.io/gh/Santtosh19/PyReliabilityPro/graph/badge.svg?token=U0P4QKPY54)](https://codecov.io/gh/Santtosh19/PyReliabilityPro)


**PyReliabilityPro** is a lightweight, open-source Python toolkit designed for engineers, data scientists, and students to perform common reliability engineering calculations and analyses. The project focuses on providing a clean, intuitive API for statistical analysis of failure data, backed by a robust, modern development workflow.

This project was developed as a comprehensive portfolio piece to showcase skills in Python software development, Test-Driven Development (TDD), Quality Assurance (QA) best practices, and CI/CD automation with GitHub Actions.

---

## Key Features

- **Weibull Distribution Analysis:**
  - **Parameter Estimation:** Estimate 2-parameter (beta, eta) or 3-parameter (beta, eta, gamma) Weibull parameters from failure data using Maximum Likelihood Estimation (MLE) via `scipy.stats`.
  - **Descriptive Functions:** Calculate the Probability Density Function (PDF), Cumulative Distribution Function (CDF), Survival Function (SF), and Hazard Function (HF).
- **Reliability Metrics:**
  - Calculate the theoretical **Mean Time To Failure (MTTF)** for a given Weibull distribution.
  - Calculate the sample MTTF for data assumed to follow an exponential distribution.
- **Exceptional Code Quality & QA Focus:**
  - **High Test Coverage:** Achieved **over 95% code coverage** with a comprehensive suite of unit tests using `pytest`. Tests cover normal functionality, edge cases, and input validations.
  - **Static Analysis:** The codebase is automatically checked for code style (`flake8`), formatting consistency (`black`), and type safety (`mypy`) on every commit.
- **Modern CI/CD Pipeline:**
  - A full-featured Continuous Integration pipeline built with **GitHub Actions**.
  - **Automated Workflow:** On every push and pull request to the `main` branch, the pipeline automatically:
    1.  Installs dependencies.
    2.  Runs linters and formatters to check code quality.
    3.  Executes the entire test suite across multiple Python versions (`3.8`, `3.9`, `3.10`, `3.11`).
    4.  Generates a code coverage report and uploads it to **Codecov** for analysis and visualization.

---

## Installation

*(Note: Once published to PyPI, this will be the primary installation method.)*

To install PyReliabilityPro, you can use `pip`:

```bash
pip install pyreliabilitypro 
```

Alternatively, to install the latest development version directly from GitHub:
```bash
pip install git+https://github.com/Santtoh19/PyReliabilityPro.git
```

## Quick Start / Usage Example
Here's a simple example of how to use the toolkit to fit a 2-parameter Weibull distribution to some failure data and then analyze it.
```bash
import pyreliabilitypro as rel
import numpy as np

# 1. Sample failure data (e.g., in hours)
failure_times = [105, 120, 135, 160, 175, 190, 210, 230, 255, 280]

# 2. Estimate the 2-parameter Weibull parameters from the data
# The weibull_fit function returns (beta, eta, gamma)
# For a 2P fit, gamma will be 0.0.
try:
    beta_est, eta_est, _ = rel.weibull_fit(failure_times)
    print(f"Estimated Beta (Shape): {beta_est:.2f}")
    print(f"Estimated Eta (Scale / Characteristic Life): {eta_est:.2f} hours")

    # 3. Use the estimated parameters to analyze reliability
    
    # Calculate the probability of failure by 150 hours (CDF)
    prob_fail_by_150 = rel.weibull_cdf(x=150, beta=beta_est, eta=eta_est)
    print(f"Probability of failure by 150 hours: {prob_fail_by_150:.2%}")

    # Calculate the reliability (probability of survival) at 150 hours (SF)
    reliability_at_150 = rel.weibull_sf(x=150, beta=beta_est, eta=eta_est)
    print(f"Reliability (survival probability) at 150 hours: {reliability_at_150:.2%}")

    # Calculate the instantaneous failure rate (hazard rate) at 150 hours
    hazard_at_150 = rel.weibull_hf(x=150, beta=beta_est, eta=eta_est)
    print(f"Hazard Rate at 150 hours: {hazard_at_150:.4f} (failures/hour)")

    # Calculate the Mean Time To Failure (MTTF) for this distribution
    mttf = rel.weibull_mttf(beta=beta_est, eta=eta_est)
    print(f"Calculated MTTF for this distribution: {mttf:.2f} hours")

except ValueError as e:
    print(f"An error occurred: {e}")
```

## Development & Contribution

This project is built with modern Python development practices. To set up a local development environment:
Clone the repository:
```bash
git clone https://github.com/Santtosh19/PyReliabilityPro.git
cd PyReliabilityPro
```

Create and activate a virtual environment:
```bash
python -m venv .venv
# On Windows (PowerShell):
# .\.venv\Scripts\Activate.ps1
# On macOS/Linux:
# source .venv/bin/activate
```
Install all dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```
Run checks and tests locally:
```bash
# Run code style and quality checks
flake8 .
black --check .
mypy pyreliabilitypro --ignore-missing-imports

# Run the full test suite
pytest
```