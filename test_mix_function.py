"""
Test the mix() function to see if that's causing the issue
"""
import sys
import numpy as np
from pathlib import Path

# Add ARTFIMA to path
artfima_path = Path(__file__).parent / "ARTFIMA"
if str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

from artfima_python.tacvf import tacvfFI, tacvfARMA, mix

print("Testing mix() function")
print("=" * 80)

d = 0.3
lambda_param = 0.025
phi = np.array([0.2])
theta = np.array([0.05])
maxlag = 20

# Compute lagTrunc
lagTrunc = 2 * max(128, 2 ** int(np.ceil(np.log2(maxlag))))
print(f"lagTrunc: {lagTrunc}")
print()

# Step 1: Compute fractional component
x = tacvfFI(d=d, lambda_param=lambda_param, maxlag=lagTrunc)
print(f"Fractional component (x):")
print(f"  Length: {len(x)}")
print(f"  x[0:5]: {x[:5]}")
print(f"  Range: [{x.min():.6f}, {x.max():.6f}]")
print()

# Step 2: Compute ARMA component
y = tacvfARMA(phi=phi, theta=theta, maxlag=lagTrunc, sigma2=1.0)
print(f"ARMA component (y):")
print(f"  Length: {len(y)}")
print(f"  y[0:5]: {y[:5]}")
print(f"  Range: [{y.min():.6f}, {y.max():.6f}]")
print()

# Step 3: Mix
print(f"Mixing...")
z = mix(x, y)
print(f"Mixed result (z):")
print(f"  Length: {len(z)}")
print(f"  z[0:5]: {z[:5]}")
print(f"  Range: [{z.min():.10e}, {z.max():.10e}]")
print()

# Expected result: z should be similar in magnitude to x and y
print(f"Analysis:")
print(f"  x[0] = {x[0]:.6f} (fractional variance)")
print(f"  y[0] = {y[0]:.6f} (ARMA variance)")
print(f"  z[0] = {z[0]:.10e} (mixed variance)")
print(f"  z[0] / (x[0] * y[0]) = {z[0] / (x[0] * y[0]):.10e}")
print()

# Try understanding the mix function
print("=" * 80)
print("Understanding mix() function behavior")
print("=" * 80)

from artfima_python.tacvf import symtacvf
from scipy.fft import fft, ifft

# Manual computation
n = 2 * len(x) - 2
sx = symtacvf(x)
sy = symtacvf(y)

print(f"Symmetric x length: {len(sx)}")
print(f"Symmetric y length: {len(sy)}")
print(f"sx[0:5]: {sx[:5]}")
print(f"sy[0:5]: {sy[:5]}")
print()

# FFT multiplication
fx = fft(sx)
fy = fft(sy)
print(f"FFT(sx) magnitude[0:5]: {np.abs(fx[:5])}")
print(f"FFT(sy) magnitude[0:5]: {np.abs(fy[:5])}")
print()

fxy = fx * fy
print(f"FFT product magnitude[0:5]: {np.abs(fxy[:5])}")
print()

result = np.real(ifft(fxy) / n)
print(f"IFFT result[0:5]: {result[:5]}")
print(f"Normalization factor (n): {n}")
