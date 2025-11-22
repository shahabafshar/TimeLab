"""
Test artfimaTACVF function with scalar parameters
"""
import sys
import numpy as np
from pathlib import Path

# Add ARTFIMA to path
artfima_path = Path(__file__).parent / "ARTFIMA"
if str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

from artfima_python.tacvf import artfimaTACVF

print("Testing artfimaTACVF function")
print("=" * 80)

# Test with scalar parameters
d = 0.3
lambda_param = 0.025
phi = np.array([0.1])
theta = np.array([0.1])
maxlag = 20
sigma2 = 1.0

print(f"Parameters:")
print(f"  d = {d} (type: {type(d)})")
print(f"  lambda_param = {lambda_param} (type: {type(lambda_param)})")
print(f"  phi = {phi} (type: {type(phi)})")
print(f"  theta = {theta} (type: {type(theta)})")
print(f"  maxlag = {maxlag}")
print(f"  sigma2 = {sigma2}")
print()

# Test artfimaTACVF
print("Calling artfimaTACVF with SCALAR parameters...")
try:
    result = artfimaTACVF(
        d=d,
        lambda_param=lambda_param,
        phi=phi,
        theta=theta,
        maxlag=maxlag,
        sigma2=sigma2
    )
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
print("Calling artfimaTACVF with NUMPY SCALAR parameters (0-d arrays)...")
d_arr = np.array(0.3)  # 0-dimensional array
lambda_arr = np.array(0.025)  # 0-dimensional array

print(f"  d = {d_arr} (type: {type(d_arr)}, ndim: {d_arr.ndim})")
print(f"  lambda_param = {lambda_arr} (type: {type(lambda_arr)}, ndim: {lambda_arr.ndim})")

try:
    result = artfimaTACVF(
        d=d_arr,
        lambda_param=lambda_arr,
        phi=phi,
        theta=theta,
        maxlag=maxlag,
        sigma2=sigma2
    )
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
