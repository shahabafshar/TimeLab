"""Simple test of ARTFIMA optimization"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Add ARTFIMA package to path
artfima_path = Path(__file__).parent / "ARTFIMA"
if str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

from artfima_python.artfima import artfima as artfima_fit

# Load data
data_path = Path(__file__).parent / "backend" / "data" / "samples" / "co2_levels.csv"
df = pd.read_csv(data_path)
z = df['co2'].values
z_diff = np.diff(z)

print("=" * 70)
print("ARTFIMA(3,d,11) Optimization Test")
print("=" * 70)
print(f"Data length: {len(z_diff)}")
print()

# Run ARTFIMA fit
result = artfima_fit(
    z=z_diff,
    glp="ARTFIMA",
    arimaOrder=(3, 0, 11),
    likAlg="exact"
)

print("Results:")
print(f"  d: {result.dHat:.6f}")
print(f"  lambda: {result.lambdaHat:.6f}")
print(f"  LL: {result.LL:.4f}")
print(f"  AIC: {result.aic:.4f}")
print(f"  BIC: {result.bic:.4f}")
print(f"  Optimizer: {result.optAlg}")
print(f"  Convergence: {result.convergence}")
print()
print(f"  phi: {result.phiHat}")
print(f"  theta: {result.thetaHat}")
print()

# Reference
print("R Reference:")
print("  d=9.999682, lambda=2.021603, LL=-915, AIC=1866")

# Check validity
print()
if np.isfinite(result.LL) and result.LL < 0:
    print("[OK] Valid log-likelihood")
else:
    print("[FAIL] Invalid log-likelihood")
