"""Test that ARTFIMA bounds are properly enforced after switching to L-BFGS-B only"""
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

# Apply differencing (same as before)
z_diff = np.diff(z)

print("=" * 70)
print("TESTING ARTFIMA(3,0,11) WITH BOUNDS ENFORCEMENT")
print("=" * 70)
print(f"Data length: {len(z_diff)}")
print(f"dMax = 10 (bounds should be enforced)")
print()

# Run ARTFIMA fit with p=3, q=11 (same as R comparison)
result = artfima_fit(
    z=z_diff,
    glp="ARTFIMA",
    arimaOrder=(3, 0, 11),
    likAlg="exact"
)

print("Results:")
print(f"  d: {result.dHat:.4f}")
print(f"  lambda: {result.lambdaHat:.4f}")
print(f"  phi: {result.phiHat}")
print(f"  theta: {result.thetaHat}")
print(f"  LL: {result.LL:.2f}")
print(f"  AIC: {result.aic:.2f}")
print(f"  BIC: {result.bic:.2f}")
print(f"  Optimizer: {result.optAlg}")
print()

# Validate bounds
dMax = 10.0
print("Bound checks:")
print(f"  d <= dMax ({dMax}): {result.dHat <= dMax} {'[OK]' if result.dHat <= dMax else '[FAIL - d exceeds bound!]'}")
print(f"  d >= 0: {result.dHat >= 0} {'[OK]' if result.dHat >= 0 else '[FAIL]'}")
print(f"  lambda >= 0: {result.lambdaHat >= 0} {'[OK]' if result.lambdaHat >= 0 else '[FAIL]'}")
print()

# R reference values
print("Comparison with R:")
print("  R found: d=9.999, lambda=2.02, LL=-915, AIC=1866")
print(f"  Python:  d={result.dHat:.3f}, lambda={result.lambdaHat:.2f}, LL={result.LL:.0f}, AIC={result.aic:.0f}")
print()

# Generate forecasts
from artfima_python.forecast import artfima_forecast
print("Generating forecasts...")
forecasts = artfima_forecast(result, h=12)
print(f"  Forecast values (h=1 to 5): {forecasts[:5]}")

# R forecast reference (approximate)
print("  R forecasts (approx): [436.75, 435.94, 435.13, ...]")

if result.dHat <= dMax:
    print("\n[OK] BOUNDS ARE PROPERLY ENFORCED")
else:
    print("\n[FAIL] d EXCEEDS BOUND - L-BFGS-B not working correctly")
