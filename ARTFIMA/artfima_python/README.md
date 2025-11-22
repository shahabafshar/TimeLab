# ARTFIMA Python Implementation

A comprehensive Python implementation of the ARTFIMA (Autoregressive Tempered Fractionally Integrated Moving Average) model, based on the R `artfima` package source code.

## Features

- **ARTFIMA Model**: Full implementation of the ARTFIMA model with tempering parameter
- **ARFIMA Model**: Special case of ARTFIMA (when lambda = 0)
- **ARMA Model**: Special case of ARTFIMA (when d = 0 and lambda = 0)
- **Exact MLE**: Maximum likelihood estimation using exact likelihood
- **Whittle MLE**: Approximate maximum likelihood using Whittle's method
- **Theoretical ACF**: Computation of theoretical autocovariance function
- **Spectral Density**: Computation of spectral density function

## Installation

The package requires:
- NumPy
- SciPy

No additional compilation is needed.

## Usage

### Basic Example

```python
import numpy as np
from artfima_python import artfima

# Generate or load time series data
z = np.random.randn(100)

# Fit ARTFIMA model
result = artfima(z, glp="ARTFIMA", arimaOrder=(1, 0, 1), likAlg="exact")

# Access results
print(f"d: {result.dHat}")
print(f"lambda: {result.lambdaHat}")
print(f"phi: {result.phiHat}")
print(f"theta: {result.thetaHat}")
print(f"Log-likelihood: {result.LL}")
print(f"AIC: {result.aic}")
print(f"BIC: {result.bic}")
```

### ARFIMA Model

```python
# Fit ARFIMA model (lambda = 0)
result = artfima(z, glp="ARFIMA", arimaOrder=(1, 0, 1), likAlg="exact")
```

### ARMA Model

```python
# Fit ARMA model (d = 0, lambda = 0)
result = artfima(z, glp="ARIMA", arimaOrder=(1, 0, 1), likAlg="exact")
```

### Using Whittle Method

```python
# Faster approximate method for large datasets
result = artfima(z, glp="ARTFIMA", arimaOrder=(1, 0, 1), likAlg="Whittle")
```

### Fixed d Parameter

```python
# Fix d parameter and estimate only lambda
result = artfima(z, glp="ARTFIMA", arimaOrder=(0, 0, 0), fixd=0.3, likAlg="exact")
```

## Model Parameters

### Function Parameters

- `z`: Time series data (array-like)
- `glp`: Model type - "ARTFIMA", "ARFIMA", or "ARIMA"
- `arimaOrder`: Tuple (p, D, q) where:
  - `p`: AR order
  - `D`: Regular differencing order
  - `q`: MA order
- `likAlg`: Likelihood algorithm - "exact" or "Whittle"
- `fixd`: Fixed value for d parameter (only for ARTFIMA)
- `b0`: Initial parameter estimates (optional)
- `lambdaMax`: Maximum value for lambda parameter (default: 3)
- `dMax`: Maximum absolute value for d parameter (default: 10)

### Result Object Attributes

- `dHat`: Estimated fractional differencing parameter
- `lambdaHat`: Estimated tempering parameter
- `phiHat`: Estimated AR coefficients
- `thetaHat`: Estimated MA coefficients
- `sigmaSq`: Innovation variance
- `LL`: Log-likelihood
- `aic`: Akaike Information Criterion
- `bic`: Bayesian Information Criterion
- `se`: Standard errors of parameters
- `convergence`: Convergence status
- `res`: Residuals
- `tacvf`: Theoretical autocovariance function

## Implementation Details

The implementation closely follows the R `artfima` package:

1. **TACVF Module**: Computes theoretical autocovariance functions for ARTFIMA, ARFIMA, and ARMA models
2. **SDF Module**: Computes spectral density functions
3. **Durbin-Levinson**: Implements exact likelihood computation using Durbin-Levinson algorithm
4. **Utils Module**: Provides AR/PACF conversion functions
5. **Main Module**: Implements the optimization and estimation logic

## Notes

- The implementation uses scipy.optimize for parameter estimation
- Multiple optimization methods are tried (BFGS, L-BFGS-B, CG, Nelder-Mead) for robustness
- The exact likelihood method uses the Durbin-Levinson algorithm for efficiency
- The Whittle method is faster but approximate

## References

Based on the R `artfima` package by A. I. McLeod, Mark M. Meerschaert, and Farzad Sabzikar.





