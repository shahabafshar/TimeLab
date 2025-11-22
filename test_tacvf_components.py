"""
Test individual TACVF components
"""
import sys
import numpy as np
from pathlib import Path

# Add ARTFIMA to path
artfima_path = Path(__file__).parent / "ARTFIMA"
if str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

from artfima_python.tacvf import tacvfFI, tacvfARMA, mix

print("Testing TACVF components separately")
print("=" * 80)

d = 0.3
lambda_param = 0.025
phi = np.array([0.1])
theta = np.array([0.1])
maxlag = 20
sigma2 = 1.0

# Compute lagTrunc (as artfimaTACVF does)
lagTrunc = 2 * max(128, 2 ** int(np.ceil(np.log2(maxlag))))
print(f"lagTrunc = {lagTrunc}")
print()

# Step 1: Compute fractional component
print("Step 1: Computing fractional component with tacvfFI...")
x = tacvfFI(d=d, lambda_param=lambda_param, maxlag=lagTrunc)
print(f"x length: {len(x)}")
print(f"x[0:10]: {x[:10]}")
print(f"x range: [{x.min():.6f}, {x.max():.6f}]")
print()

# Step 2: Compute ARMA component
print("Step 2: Computing ARMA component with tacvfARMA...")
y = tacvfARMA(phi=phi, theta=theta, maxlag=lagTrunc, sigma2=1.0)
print(f"y length: {len(y)}")
print(f"y[0:10]: {y[:10]}")
print(f"y range: [{y.min():.6f}, {y.max():.6f}]")
print()

# Step 3: Mix them
print("Step 3: Mixing x and y...")
print(f"Before mix:")
print(f"  x shape: {x.shape}, range: [{x.min():.6f}, {x.max():.6f}]")
print(f"  y shape: {y.shape}, range: [{y.min():.6f}, {y.max():.6f}]")

z = mix(x, y)
print(f"After mix:")
print(f"  z length: {len(z)}")
print(f"  z[0:10]: {z[:10]}")
print(f"  z range: [{z.min():.10f}, {z.max():.10f}]")
print()

# Step 4: Apply sigma2 and truncate
print("Step 4: Applying sigma2 and truncating...")
result = sigma2 * z[:(maxlag + 1)]
print(f"Final result:")
print(f"  length: {len(result)}")
print(f"  result[0:10]: {result[:10]}")
print(f"  result range: [{result.min():.10f}, {result.max():.10f}]")
