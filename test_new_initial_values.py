"""
Test new initial values
"""
import sys
import numpy as np
from pathlib import Path

# Add ARTFIMA to path
artfima_path = Path(__file__).parent / "ARTFIMA"
if str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

from artfima_python.tacvf import tacvfARMA
from artfima_python.utils import ARToPacf

print("Testing new initial values")
print("=" * 80)

# Compute initial phi and theta using same logic as artfima.py
p = 1
q = 1

phiInit = ARToPacf(np.tile([0.1, -0.05], (p + 1) // 2)[:p])
thetaInit = ARToPacf(np.tile([0.7, -0.5], (q + 1) // 2)[:q])

print(f"AR PACF init: [0.1]")
print(f"AR coeff (phi): {phiInit}")
print()
print(f"MA PACF init: [0.7]")
print(f"MA coeff (theta): {thetaInit}")
print()

# Test TACVF with these values
result = tacvfARMA(phi=phiInit, theta=thetaInit, maxlag=20, sigma2=1.0)

print(f"ARMA TACVF:")
print(f"  result[0:10]: {result[:10]}")
print(f"  Is white noise: {np.all(np.abs(result[1:]) < 1e-10)}")
print(f"  Has autocorrelation: {np.any(np.abs(result[1:]) > 0.01)}")
