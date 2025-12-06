"""Debug the Entropy function for different starting points"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Add ARTFIMA package to path
artfima_path = Path(__file__).parent / "ARTFIMA"
if str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

from artfima_python.tacvf import artfimaTACVF
from artfima_python.durbin_levinson import DLLoglikelihood
from artfima_python.utils import PacfToAR

# Load data
data_path = Path(__file__).parent / "backend" / "data" / "samples" / "co2_levels.csv"
df = pd.read_csv(data_path)
z = df['co2'].values
z_diff = np.diff(z)
w = z_diff - np.mean(z_diff)  # Center data
n = len(w)

print("=" * 70)
print("DEBUG: Testing Entropy function at different starting points")
print("=" * 70)
print(f"Data length: {n}")
print()

# Define p, q
p, q = 3, 11

# Test different starting points
def test_starting_point(name, d, lambda_param, phi_pacf, theta_pacf):
    print(f"\n--- {name} ---")
    print(f"d={d}, lambda={lambda_param}")
    print(f"phi_pacf={phi_pacf[:3]}... (len={len(phi_pacf)})")
    print(f"theta_pacf={theta_pacf[:3]}... (len={len(theta_pacf)})")

    # Check PACF bounds
    if np.any(np.abs(phi_pacf) >= 1.0):
        print("  [FAIL] phi PACF has values >= 1")
        return np.inf
    if np.any(np.abs(theta_pacf) >= 1.0):
        print("  [FAIL] theta PACF has values >= 1")
        return np.inf

    # Convert PACF to AR/MA
    try:
        phi = PacfToAR(phi_pacf)
        theta = PacfToAR(theta_pacf)
        print(f"  phi (AR)={phi[:3]}...")
        print(f"  theta (MA)={theta[:3]}...")
    except Exception as e:
        print(f"  [FAIL] PacfToAR error: {e}")
        return np.inf

    # Compute TACVF
    try:
        r = artfimaTACVF(d=d, lambda_param=lambda_param, phi=phi, theta=theta, maxlag=n-1)
        print(f"  TACVF[0]={r[0]:.6f}, has_nan={np.any(np.isnan(r))}, has_inf={np.any(np.isinf(r))}")
        if r[0] <= 0:
            print(f"  [FAIL] r[0] <= 0 (invalid variance)")
            return np.inf
        if not np.all(np.isfinite(r)):
            print(f"  [FAIL] TACVF has non-finite values")
            return np.inf
    except Exception as e:
        print(f"  [FAIL] TACVF error: {e}")
        return np.inf

    # Compute log-likelihood
    try:
        ll = DLLoglikelihood(r, w)
        print(f"  DLLoglikelihood={ll:.4f}, is_finite={np.isfinite(ll)}")
        if not np.isfinite(ll):
            print(f"  [FAIL] LL is not finite")
            return np.inf
        negLL = -ll
        if negLL < 0:
            print(f"  [FAIL] negLL < 0 (invalid)")
            return np.inf
        print(f"  [OK] negLL={negLL:.4f}")
        return negLL
    except Exception as e:
        print(f"  [FAIL] DLLoglikelihood error: {e}")
        return np.inf

# Test 1: R-like starting point
phi_pacf_r = np.tile([-0.5, -0.3], (p + 1) // 2)[:p]
theta_pacf_r = np.tile([0.3, 0.2, -0.2, -0.1], (q + 3) // 4)[:q]
test_starting_point("R-like (d=8, lambda=1.5)", 8.0, 1.5, phi_pacf_r, theta_pacf_r)

# Test 2: Low d starting point (R defaults)
phi_pacf_low = np.tile([0.1, -0.05], (p + 1) // 2)[:p]
theta_pacf_low = np.tile([0.1, -0.1], (q + 1) // 2)[:q]
test_starting_point("Low d (d=0.3, lambda=0.025)", 0.3, 0.025, phi_pacf_low, theta_pacf_low)

# Test 3: Medium d
phi_pacf_med = np.tile([0.2, -0.1], (p + 1) // 2)[:p]
theta_pacf_med = np.tile([0.2, -0.15], (q + 1) // 2)[:q]
test_starting_point("Medium d (d=3, lambda=0.8)", 3.0, 0.8, phi_pacf_med, theta_pacf_med)

# Test 4: R's optimal values (from R output)
# Convert R's AR/MA to PACF to use as starting point
print("\n" + "=" * 70)
print("Testing with R's ACTUAL optimal phi/theta as starting values")
print("=" * 70)

# R's optimal AR/MA coefficients
phi_r = np.array([-1.692132, -0.6944333, 0.08887375])
theta_r = np.array([-0.2645191, 0.7208977, 0.02223315, 0.2195057, 0.5952384,
                   0.1984419, 0.1996436, -0.03327467, -0.1814059, -0.3054669, -0.2574475])

# Compute TACVF with R's optimal values directly
try:
    r = artfimaTACVF(d=9.999, lambda_param=2.02, phi=phi_r, theta=theta_r, maxlag=n-1)
    print(f"R's optimal -> TACVF[0]={r[0]:.6f}")
    if np.all(np.isfinite(r)) and r[0] > 0:
        ll = DLLoglikelihood(r, w)
        print(f"R's optimal -> LL={ll:.2f}, -LL={-ll:.2f}")
        print(f"R claims LL=-915, we get LL={ll:.2f}")
    else:
        print(f"R's optimal -> Invalid TACVF")
except Exception as e:
    print(f"R's optimal -> Error: {e}")

# Test 5: Try different d values to find where valid LL exists
print("\n" + "=" * 70)
print("Scanning d values to find valid region")
print("=" * 70)

for d in [0.5, 1.0, 2.0, 5.0, 8.0, 9.0, 9.5, 9.9]:
    for lam in [0.1, 0.5, 1.0, 2.0]:
        try:
            r = artfimaTACVF(d=d, lambda_param=lam, phi=phi_r, theta=theta_r, maxlag=n-1)
            if np.all(np.isfinite(r)) and r[0] > 0:
                ll = DLLoglikelihood(r, w)
                if np.isfinite(ll) and ll < 0:  # Valid LL should be negative
                    print(f"d={d}, lam={lam}: LL={ll:.2f} [VALID]")
        except:
            pass
