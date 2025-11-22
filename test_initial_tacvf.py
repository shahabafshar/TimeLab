"""
Check TACVF for initial parameters
"""
import sys
import numpy as np
from pathlib import Path

# Add ARTFIMA to path
artfima_path = Path(__file__).parent / "ARTFIMA"
if str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

from artfima_python.tacvf import artfimaTACVF

print("Testing ARTFIMA TACVF with INITIAL parameters")
print("=" * 80)

# Initial parameters (from artfima.py after my changes)
d = 0.3
lambda_param = 0.025
phi = np.array([0.1])
theta = np.array([0.7])
maxlag = 20

print(f"Parameters:")
print(f"  d: {d}")
print(f"  lambda: {lambda_param}")
print(f"  phi: {phi}")
print(f"  theta: {theta}")
print()

# Compute TACVF
tacvf = artfimaTACVF(
    d=d,
    lambda_param=lambda_param,
    phi=phi,
    theta=theta,
    maxlag=maxlag,
    sigma2=1.0
)

print(f"ARTFIMA TACVF:")
print(f"  Length: {len(tacvf)}")
print(f"  tacvf[0:10]: {tacvf[:10]}")
print(f"  Range: [{tacvf.min():.6e}, {tacvf.max():.6e}]")
print(f"  tacvf[0] (variance): {tacvf[0]:.6f}")
print()

# Check if it's reasonable
is_positive = tacvf[0] > 0
is_reasonable = 0.1 < tacvf[0] < 10  # Should be order of magnitude 1
has_structure = np.any(np.abs(tacvf[1:5]) > 0.01)

print(f"Validation:")
print(f"  tacvf[0] > 0: {is_positive}")
print(f"  tacvf[0] in reasonable range (0.1, 10): {is_reasonable}")
print(f"  Has autocorrelation structure: {has_structure}")

if all([is_positive, is_reasonable, has_structure]):
    print(f"\n[OK] Initial TACVF looks good!")
else:
    print(f"\n[FAIL] Initial TACVF has issues!")
