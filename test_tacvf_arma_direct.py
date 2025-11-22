"""
Direct test of tacvfARMA with new code
"""
import sys
import numpy as np
from pathlib import Path

# Add ARTFIMA to path
artfima_path = Path(__file__).parent / "ARTFIMA"
if str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

from artfima_python.tacvf import tacvfARMA

print("Testing tacvfARMA with phi=[0.2], theta=[0.05]")
print("=" * 80)

phi = np.array([0.2])
theta = np.array([0.05])
maxlag = 20

result = tacvfARMA(phi=phi, theta=theta, maxlag=maxlag, sigma2=1.0)

print(f"Result: {result}")
print(f"Result[0]: {result[0]}")
print(f"Is essentially white noise: {np.all(np.abs(result[1:]) < 1e-10)}")

# Also test if statsmodels is being imported
print("\nChecking if statsmodels is being used:")
try:
    from statsmodels.tsa.arima_process import arma_acovf
    print("  statsmodels is available!")

    ar_params = -phi
    ma_params = theta
    result_sm = arma_acovf(ar_params, ma_params, nobs=maxlag+1, sigma2=1.0)
    print(f"  statsmodels result: {result_sm[:5]}")

except ImportError as e:
    print(f"  statsmodels is NOT available: {e}")
