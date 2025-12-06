"""
Debug script to verify Python ARTFIMA optimizer is actually running
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Add ARTFIMA package to path
artfima_path = Path(__file__).parent / "ARTFIMA"
if str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

# Load data
data_path = Path(__file__).parent / "backend" / "data" / "samples" / "co2_levels.csv"
df = pd.read_csv(data_path)
z = df['co2'].values

# Apply differencing
z_diff = np.diff(z)

print(f"Data length after differencing: {len(z_diff)}")
print(f"Last original value: {z[-1]:.4f}")

# Import the artfima module
from artfima_python.artfima import artfima as artfima_fit
from artfima_python.tacvf import artfimaTACVF
from artfima_python.durbin_levinson import DLLoglikelihood
from artfima_python.utils import PacfToAR, ARToPacf

# Test 1: Check if TACVF calculation works correctly
print("\n" + "="*60)
print("TEST 1: TACVF Calculation")
print("="*60)

# With initial parameters
d_init = 0.3
lambda_init = 0.025
phi_init = np.array([0.1, -0.05, 0.1])  # p=3
theta_init = np.array([0.7, -0.5, 0.7, -0.5, 0.7, -0.5, 0.7, -0.5, 0.7, -0.5, 0.7])  # q=11

r_init = artfimaTACVF(d=d_init, lambda_param=lambda_init,
                      phi=phi_init, theta=theta_init, maxlag=len(z_diff)-1)
print(f"TACVF at initial params (first 5): {r_init[:5]}")
print(f"TACVF contains NaN: {np.any(np.isnan(r_init))}")
print(f"TACVF contains Inf: {np.any(np.isinf(r_init))}")

# Test 2: Check likelihood at initial params
print("\n" + "="*60)
print("TEST 2: Likelihood Calculation")
print("="*60)

w = z_diff - np.mean(z_diff)  # Center data
ll_init = DLLoglikelihood(r_init, w)
print(f"Log-likelihood at initial params: {ll_init:.4f}")

# Test 3: Try different parameter values and check likelihood
print("\n" + "="*60)
print("TEST 3: Likelihood at Different Parameters")
print("="*60)

test_params = [
    (0.3, 0.025, "Initial values"),
    (0.5, 0.1, "d=0.5, lambda=0.1"),
    (1.0, 0.5, "d=1.0, lambda=0.5"),
    (2.0, 1.0, "d=2.0, lambda=1.0"),
    (5.0, 1.5, "d=5.0, lambda=1.5"),
    (9.0, 2.0, "d=9.0, lambda=2.0 (close to R result)"),
]

for d, lam, desc in test_params:
    try:
        r = artfimaTACVF(d=d, lambda_param=lam, phi=phi_init, theta=theta_init, maxlag=len(z_diff)-1)
        if np.all(np.isfinite(r)):
            ll = DLLoglikelihood(r, w)
            aic = -2 * ll + 2 * (2 + 3 + 11)  # 2 params (d, lambda) + 3 AR + 11 MA
            print(f"{desc}: LL={ll:.2f}, AIC={aic:.2f}")
        else:
            print(f"{desc}: TACVF contains non-finite values")
    except Exception as e:
        print(f"{desc}: Error - {e}")

# Test 4: Actually run the optimizer with debug output
print("\n" + "="*60)
print("TEST 4: Running Full ARTFIMA Optimizer")
print("="*60)

result = artfima_fit(
    z=z_diff,
    glp="ARTFIMA",
    arimaOrder=(3, 0, 11),
    likAlg="exact"
)

print(f"Estimated d: {result.dHat}")
print(f"Estimated lambda: {result.lambdaHat}")
print(f"Log-likelihood: {result.LL}")
print(f"AIC: {result.aic}")
print(f"BIC: {result.bic}")
print(f"Convergence: {result.convergence}")
print(f"Optimization algorithm: {result.optAlg}")
print(f"AR coefficients (phi): {result.phiHat}")
print(f"MA coefficients (theta): {result.thetaHat}")

# Test 5: Check if result.x from optimization matches returned values
print("\n" + "="*60)
print("TEST 5: Parameter Analysis")
print("="*60)
print(f"Are d and lambda exactly equal to initial values?")
print(f"  d init=0.3, result={result.dHat}: {'SAME!' if abs(result.dHat - 0.3) < 1e-6 else 'Different'}")
print(f"  lambda init=0.025, result={result.lambdaHat}: {'SAME!' if abs(result.lambdaHat - 0.025) < 1e-6 else 'Different'}")
