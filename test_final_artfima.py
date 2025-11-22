"""
Final test of ARTFIMA with all fixes
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Add ARTFIMA to path
artfima_path = Path(__file__).parent / "ARTFIMA"
if str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

print("=" * 80)
print("FINAL TEST: ARTFIMA WITH ALL FIXES")
print("=" * 80)

# Test 1: Verify tacvfARMA works with phi != theta
from artfima_python.tacvf import tacvfARMA

print("\n1. Testing tacvfARMA with phi=0.9, theta=0.1:")
result = tacvfARMA(phi=np.array([0.9]), theta=np.array([0.1]), maxlag=10, sigma2=1.0)
print(f"   TACVF[0:5]: {result[:5]}")
is_wn = np.all(np.abs(result[1:]) < 1e-10)
print(f"   Is white noise: {is_wn}")
print(f"   Expected: NOT white noise")

# Test 2: Run full ARTFIMA fit on CO2 data
from artfima_python import artfima as artfima_fit

print("\n2. Running ARTFIMA fit on CO2 data...")
co2_path = Path(__file__).parent / "backend" / "data" / "samples" / "co2_levels.csv"
df = pd.read_csv(co2_path)
z = df['co2'].values[:100]  # Use first 100 points

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

print(f"\n3. Results:")
print(f"   d: {result.dHat}")
print(f"   lambda: {result.lambdaHat}")
print(f"   phi: {result.phiHat}")
print(f"   theta: {result.thetaHat}")
print(f"   sigmaSq: {result.sigmaSq}")
print(f"   LL: {result.LL}")
print(f"   AIC: {result.aic}")
print(f"   BIC: {result.bic}")

# Check if results are reasonable
print(f"\n4. Validation:")
is_sigma_positive = result.sigmaSq > 0
is_ll_reasonable = -10000 < result.LL < 0  # LL should be negative but not huge
is_aic_reasonable = 0 < result.aic < 1000  # AIC should be positive and reasonable
is_params_moved = not (np.allclose(result.dHat, 0.3) and np.allclose(result.lambdaHat, 0.025))

print(f"   sigmaSq > 0: {is_sigma_positive} [OK]" if is_sigma_positive else f"   sigmaSq > 0: {is_sigma_positive} [FAIL]")
print(f"   LL in reasonable range: {is_ll_reasonable} [OK]" if is_ll_reasonable else f"   LL in reasonable range: {is_ll_reasonable} [FAIL]")
print(f"   AIC in reasonable range: {is_aic_reasonable} [OK]" if is_aic_reasonable else f"   AIC in reasonable range: {is_aic_reasonable} [FAIL]")
print(f"   Parameters moved from initial: {is_params_moved} [OK]" if is_params_moved else f"   Parameters moved from initial: {is_params_moved} [FAIL]")

if all([is_sigma_positive, is_ll_reasonable, is_aic_reasonable, is_params_moved]):
    print(f"\n[OK] ALL CHECKS PASSED - ARTFIMA IS WORKING CORRECTLY!")
else:
    print(f"\n[FAIL] SOME CHECKS FAILED - ISSUES REMAIN")
