"""
Understand the core issue
"""
import sys
import numpy as np
from pathlib import Path

# Add ARTFIMA to path
artfima_path = Path(__file__).parent / "ARTFIMA"
if str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

# First, let's understand what parameters are ACTUALLY being optimized
print("=" * 80)
print("RE-RUNNING ARTFIMA FIT ON CO2 DATA TO SEE ACTUAL PARAMETERS")
print("=" * 80)

import pandas as pd
from artfima_python import artfima as artfima_fit

# Load CO2 data
co2_path = Path(__file__).parent / "backend" / "data" / "samples" / "co2_levels.csv"
df = pd.read_csv(co2_path)
z = df['co2'].values[:100]  # Use first 100 points for faster testing

print(f"Data length: {len(z)}")
print(f"Data mean: {z.mean():.2f}")
print()

# Fit with different initial conditions
print("Fitting ARTFIMA(1,d,1) model...")
result = artfima_fit(
    z=z,
    glp="ARTFIMA",
    arimaOrder=(1, 0, 1),
    likAlg="exact",
    fixd=None,
    b0=None,
    lambdaMax=3,
    dMax=10
)

print(f"\nFitted parameters:")
print(f"  d: {result.dHat}")
print(f"  lambda: {result.lambdaHat}")
print(f"  phi (AR): {result.phiHat}")
print(f"  theta (MA): {result.thetaHat}")
print(f"  sigmaSq: {result.sigmaSq}")
print(f"  LL: {result.LL}")

print(f"\nRaw optimization parameters (bHat):")
print(f"  {result.bHat}")

# Check if phi ≈ theta
if result.phiHat is not None and result.thetaHat is not None and len(result.phiHat) > 0 and len(result.thetaHat) > 0:
    phi_val = result.phiHat[0]
    theta_val = result.thetaHat[0]
    print(f"\nAre phi and theta equal? phi={phi_val:.6f}, theta={theta_val:.6f}")
    print(f"Difference: {abs(phi_val - theta_val):.6e}")

# Now let's manually test the TACVF computation
print("\n" + "=" * 80)
print("TESTING TACVF WITH FITTED PARAMETERS")
print("=" * 80)

from artfima_python.tacvf import artfimaTACVF

if result.phiHat is not None and result.thetaHat is not None:
    tacvf = artfimaTACVF(
        d=float(result.dHat) if isinstance(result.dHat, (int, float, np.number)) else result.dHat,
        lambda_param=float(result.lambdaHat) if isinstance(result.lambdaHat, (int, float, np.number)) else result.lambdaHat,
        phi=result.phiHat,
        theta=result.thetaHat,
        maxlag=20,
        sigma2=1.0
    )
    print(f"TACVF[0:10]: {tacvf[:10]}")
    print(f"TACVF range: [{tacvf.min():.6e}, {tacvf.max():.6e}]")

# Try fitting with different model orders
print("\n" + "=" * 80)
print("TESTING WITH ARFIMA (no tempering)")
print("=" * 80)

result2 = artfima_fit(
    z=z,
    glp="ARFIMA",
    arimaOrder=(1, 0, 1),
    likAlg="exact"
)

print(f"\nARFIMA fitted parameters:")
print(f"  d: {result2.dHat}")
print(f"  phi: {result2.phiHat}")
print(f"  theta: {result2.thetaHat}")
print(f"  sigmaSq: {result2.sigmaSq}")
print(f"  LL: {result2.LL}")
print(f"  AIC: {result2.aic}")
