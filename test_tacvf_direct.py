"""
Direct test of tacvfFI function
"""
import sys
import numpy as np
from pathlib import Path

# Add ARTFIMA to path
artfima_path = Path(__file__).parent / "ARTFIMA"
if str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

from artfima_python.tacvf import tacvfFI, tacvfFDWN

print("Testing tacvfFI function")
print("=" * 80)

d = 0.3
lambda_param = 0.025
maxlag = 20
sigma2 = 1.0

print(f"Parameters:")
print(f"  d = {d} (type: {type(d)})")
print(f"  lambda_param = {lambda_param} (type: {type(lambda_param)})")
print(f"  maxlag = {maxlag}")
print(f"  sigma2 = {sigma2}")
print()

# Test tacvfFI
print("Calling tacvfFI...")
try:
    result = tacvfFI(d=d, lambda_param=lambda_param, maxlag=maxlag, sigma2=sigma2)
    print(f"Result length: {len(result)}")
    print(f"Result[0:10]: {result[:10]}")
    print(f"Result range: [{result.min():.6f}, {result.max():.6f}]")
    print(f"Any NaN: {np.any(np.isnan(result))}")
    print(f"Any Inf: {np.any(np.isinf(result))}")
    print(f"Any negative: {np.any(result < 0)}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("Testing tacvfFDWN function")
print("=" * 80)

dfrac = 0.3
print(f"Parameters:")
print(f"  dfrac = {dfrac} (type: {type(dfrac)})")
print(f"  maxlag = {maxlag}")
print(f"  sigma2 = {sigma2}")
print()

# Test tacvfFDWN
print("Calling tacvfFDWN...")
try:
    result = tacvfFDWN(dfrac=dfrac, maxlag=maxlag, sigma2=sigma2)
    print(f"Result length: {len(result)}")
    print(f"Result[0:10]: {result[:10]}")
    print(f"Result range: [{result.min():.6f}, {result.max():.6f}]")
    print(f"Any NaN: {np.any(np.isnan(result))}")
    print(f"Any Inf: {np.any(np.isinf(result))}")
    print(f"Any negative: {np.any(result < 0)}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
