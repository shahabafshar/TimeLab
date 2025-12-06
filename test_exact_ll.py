"""Test exactLoglikelihood with boundary parameters"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

artfima_path = Path(__file__).parent / "ARTFIMA"
if str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

from artfima_python.tacvf import artfimaTACVF
from artfima_python.durbin_levinson import exactLoglikelihood, DLLoglikelihood
from artfima_python.utils import PacfToAR

# Load data
data_path = Path(__file__).parent / "backend" / "data" / "samples" / "co2_levels.csv"
df = pd.read_csv(data_path)
z = df['co2'].values
z_diff = np.diff(z)
w = z_diff - np.mean(z_diff)
n = len(w)

print(f"Data: n={n}")
print(f"w variance: {np.var(w)}")

# Test with boundary params that Python found
print("\n=== Boundary params (d=10, lambda=3) ===")
d = 10.0
lambda_param = 3.0

# The PACF values from optimization result
phi_pacf = np.array([0.99, 0.999801, -0.99])
theta_pacf = np.array([-0.99] * 11)

phi = PacfToAR(phi_pacf)
theta = PacfToAR(theta_pacf)

print(f"phi: {phi[:3]}")
print(f"theta (first 3): {theta[:3]}")

r = artfimaTACVF(d=d, lambda_param=lambda_param, phi=phi, theta=theta, maxlag=n-1)
print(f"r[0]: {r[0]:.6e}")
print(f"r[1]: {r[1]:.6e}")
print(f"len(r): {len(r)}")

# Test DLLoglikelihood
print("\n--- DLLoglikelihood ---")
ll_dl = DLLoglikelihood(r, w)
print(f"DLLoglikelihood: {ll_dl}")

# Test exactLoglikelihood
print("\n--- exactLoglikelihood ---")
try:
    result = exactLoglikelihood(r, w)
    print(f"LL: {result['LL']}")
    print(f"sigmaSq: {result['sigmaSq']}")
except Exception as e:
    print(f"Error: {e}")

# Check what happens step by step
print("\n--- Step by step ---")
from scipy.linalg import toeplitz
R = toeplitz(r[:n])
print(f"R[0,0]: {R[0,0]:.6e}")
print(f"R condition number: {np.linalg.cond(R):.6e}")

try:
    L = np.linalg.cholesky(R)
    print(f"Cholesky succeeded")
    print(f"L[0,0]: {L[0,0]:.6e}")
    logdet = 2 * np.sum(np.log(np.diag(L)))
    print(f"logdet: {logdet:.6e}")
    y = np.linalg.solve(L, w)
    print(f"y[0:3]: {y[:3]}")
    quad = np.dot(y, y)
    print(f"quad: {quad:.6e}")
    LL = -0.5 * (n * np.log(2 * np.pi) + logdet + quad)
    print(f"Final LL: {LL:.6e}")
except np.linalg.LinAlgError as e:
    print(f"Cholesky failed: {e}")
