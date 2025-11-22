"""
Example usage of the ARTFIMA Python implementation
"""

import numpy as np
from artfima import artfima

# Generate sample time series data
np.random.seed(42)
n = 200
z = np.cumsum(np.random.randn(n)) + 0.1 * np.random.randn(n)

print("=" * 60)
print("ARTFIMA Python Implementation Example")
print("=" * 60)
print(f"\nTime series length: {n}")
print(f"Mean: {np.mean(z):.4f}, Std: {np.std(z):.4f}\n")

# Example 1: Fit ARTFIMA(1,0,1) model
print("Example 1: Fitting ARTFIMA(1,0,1) model")
print("-" * 60)
try:
    result1 = artfima(z, glp="ARTFIMA", arimaOrder=(1, 0, 1), likAlg="exact")
    print(f"Convergence: {result1.convergence}")
    print(f"d: {result1.dHat:.6f}")
    print(f"lambda: {result1.lambdaHat:.6f}")
    print(f"phi: {result1.phiHat}")
    print(f"theta: {result1.thetaHat}")
    print(f"sigma^2: {result1.sigmaSq:.6f}")
    print(f"Log-likelihood: {result1.LL:.4f}")
    print(f"AIC: {result1.aic:.4f}")
    print(f"BIC: {result1.bic:.4f}")
    print(f"Optimization method: {result1.optAlg}")
except Exception as e:
    print(f"Error: {e}")

print("\n")

# Example 2: Fit ARFIMA(1,0,1) model
print("Example 2: Fitting ARFIMA(1,0,1) model")
print("-" * 60)
try:
    result2 = artfima(z, glp="ARFIMA", arimaOrder=(1, 0, 1), likAlg="exact")
    print(f"Convergence: {result2.convergence}")
    print(f"d: {result2.dHat:.6f}")
    print(f"phi: {result2.phiHat}")
    print(f"theta: {result2.thetaHat}")
    print(f"sigma^2: {result2.sigmaSq:.6f}")
    print(f"Log-likelihood: {result2.LL:.4f}")
    print(f"AIC: {result2.aic:.4f}")
    print(f"BIC: {result2.bic:.4f}")
except Exception as e:
    print(f"Error: {e}")

print("\n")

# Example 3: Fit ARMA(1,1) model
print("Example 3: Fitting ARMA(1,1) model")
print("-" * 60)
try:
    result3 = artfima(z, glp="ARIMA", arimaOrder=(1, 0, 1), likAlg="exact")
    print(f"Convergence: {result3.convergence}")
    print(f"phi: {result3.phiHat}")
    print(f"theta: {result3.thetaHat}")
    print(f"sigma^2: {result3.sigmaSq:.6f}")
    print(f"Log-likelihood: {result3.LL:.4f}")
    print(f"AIC: {result3.aic:.4f}")
    print(f"BIC: {result3.bic:.4f}")
except Exception as e:
    print(f"Error: {e}")

print("\n")

# Example 4: Use Whittle method (faster for large datasets)
print("Example 4: Fitting ARTFIMA(0,0,0) using Whittle method")
print("-" * 60)
try:
    result4 = artfima(z, glp="ARTFIMA", arimaOrder=(0, 0, 0), likAlg="Whittle")
    print(f"Convergence: {result4.convergence}")
    print(f"d: {result4.dHat:.6f}")
    print(f"lambda: {result4.lambdaHat:.6f}")
    print(f"sigma^2: {result4.sigmaSq:.6f}")
    print(f"Log-likelihood: {result4.LL:.4f}")
    print(f"AIC: {result4.aic:.4f}")
    print(f"BIC: {result4.bic:.4f}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("Examples completed!")
print("=" * 60)





