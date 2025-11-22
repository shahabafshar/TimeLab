"""
Test tacvfARMA with different parameter values
"""
import sys
import numpy as np
from pathlib import Path

# Add ARTFIMA to path
artfima_path = Path(__file__).parent / "ARTFIMA"
if str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

from artfima_python.tacvf import tacvfARMA

print("Testing tacvfARMA with different parameter values")
print("=" * 80)

maxlag = 10
sigma2 = 1.0

test_cases = [
    ("AR(1) phi=0.5", np.array([0.5]), None),
    ("MA(1) theta=0.5", None, np.array([0.5])),
    ("ARMA(1,1) phi=0.5, theta=0.5", np.array([0.5]), np.array([0.5])),
    ("ARMA(1,1) phi=0.1, theta=0.1", np.array([0.1]), np.array([0.1])),
    ("ARMA(1,1) phi=0.9, theta=0.1", np.array([0.9]), np.array([0.1])),
    ("ARMA(1,1) phi=0.1, theta=0.9", np.array([0.1]), np.array([0.9])),
]

for name, phi, theta in test_cases:
    print(f"\n{name}:")
    result = tacvfARMA(phi=phi, theta=theta, maxlag=maxlag, sigma2=sigma2)
    print(f"  TACVF[0:5]: {result[:5]}")
    print(f"  Range: [{result.min():.6f}, {result.max():.6f}]")
    print(f"  All zeros (except [0]): {np.all(np.abs(result[1:]) < 1e-10)}")

# Let's also check what happens with the fitted parameters from the actual model
# In the debug output, we had phi=[0.1] and theta=[0.1]
# But these are after PacfToAR conversion
print("\n" + "=" * 80)
print("Understanding the parameter conversion")
print("=" * 80)

from artfima_python.utils import PacfToAR, ARToPacf

# If the optimization found pacf values, what would the AR/MA coefficients be?
pacf_phi = 0.1
pacf_theta = 0.1

phi_ar = PacfToAR(np.array([pacf_phi]))
theta_ma = PacfToAR(np.array([pacf_theta]))

print(f"PACF phi: {pacf_phi} -> AR coeff: {phi_ar}")
print(f"PACF theta: {pacf_theta} -> MA coeff: {theta_ma}")

# Now test with these
print(f"\nTesting with converted AR/MA coefficients:")
result = tacvfARMA(phi=phi_ar, theta=theta_ma, maxlag=maxlag, sigma2=sigma2)
print(f"  TACVF[0:5]: {result[:5]}")
