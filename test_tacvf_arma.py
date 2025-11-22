"""
Test tacvfARMA function in detail
"""
import sys
import numpy as np
from pathlib import Path

# Add ARTFIMA to path
artfima_path = Path(__file__).parent / "ARTFIMA"
if str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

from artfima_python.tacvf import tacvfARMA

print("Testing tacvfARMA function")
print("=" * 80)

phi = np.array([0.1])
theta = np.array([0.1])
maxlag = 20
sigma2 = 1.0

print(f"Parameters:")
print(f"  phi = {phi} (length: {len(phi)})")
print(f"  theta = {theta} (length: {len(theta)})")
print(f"  maxlag = {maxlag}")
print(f"  sigma2 = {sigma2}")
print()

# Test tacvfARMA
print("Calling tacvfARMA...")
result = tacvfARMA(phi=phi, theta=theta, maxlag=maxlag, sigma2=sigma2)
print(f"Result length: {len(result)}")
print(f"Result: {result}")
print(f"Result range: [{result.min():.6f}, {result.max():.6f}]")
print()

# Test with no phi/theta (white noise)
print("Testing with no AR/MA (white noise)...")
result_wn = tacvfARMA(phi=None, theta=None, maxlag=maxlag, sigma2=sigma2)
print(f"White noise TACVF: {result_wn[:10]}")
print()

# Test with only AR
print("Testing with only AR(1) phi=[0.1]...")
result_ar = tacvfARMA(phi=phi, theta=None, maxlag=maxlag, sigma2=sigma2)
print(f"AR(1) TACVF: {result_ar[:10]}")
print()

# Test with only MA
print("Testing with only MA(1) theta=[0.1]...")
result_ma = tacvfARMA(phi=None, theta=theta, maxlag=maxlag, sigma2=sigma2)
print(f"MA(1) TACVF: {result_ma[:10]}")
