"""Test initial values computation"""
import sys
import numpy as np
from pathlib import Path

# Add ARTFIMA package to path
artfima_path = Path(__file__).parent / "ARTFIMA"
if str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

# Parameters
p, q = 3, 11
glpOrder = 2
glpAdd = 2
nbeta = glpAdd + p + q

def create_initial_values(d_init, lambda_init, phi_pattern, theta_pattern):
    """Create initial parameter vector with given starting values."""
    init = np.zeros(nbeta)
    if glpOrder == 2:
        init[0] = d_init
        init[1] = lambda_init

    if p > 0:
        init[glpAdd:(p + glpAdd)] = np.tile(phi_pattern, (p + 1) // 2)[:p]
    if q > 0:
        init[(p + glpAdd):(p + q + glpAdd)] = np.tile(theta_pattern, (q + 1) // 2)[:q]
    return init

print("Testing initial values as used in artfima.py:")
print()

# Low d (as in artfima.py)
init_low = create_initial_values(0.3, 0.025, [0.1, -0.05], [0.1, -0.1])
print("low_d initialization:")
print(f"  d={init_low[0]}, lambda={init_low[1]}")
print(f"  phi PACF: {init_low[glpAdd:(p + glpAdd)]}")
print(f"  theta PACF: {init_low[(p + glpAdd):]}")
print(f"  All within (-1, 1): {np.all(np.abs(init_low[glpAdd:]) < 1)}")

# R-like
init_r = np.zeros(nbeta)
init_r[0] = 8.0
init_r[1] = 1.5
phi_pacf_r = np.tile([-0.5, -0.3], (p + 1) // 2)[:p]
init_r[glpAdd:(p + glpAdd)] = phi_pacf_r
theta_pacf_r = np.tile([0.3, 0.2, -0.2, -0.1], (q + 3) // 4)[:q]
init_r[(p + glpAdd):(p + q + glpAdd)] = theta_pacf_r

print()
print("r_like initialization:")
print(f"  d={init_r[0]}, lambda={init_r[1]}")
print(f"  phi PACF: {init_r[glpAdd:(p + glpAdd)]}")
print(f"  theta PACF: {init_r[(p + glpAdd):]}")
print(f"  All within (-1, 1): {np.all(np.abs(init_r[glpAdd:]) < 1)}")

# Test Entropy at these points
from artfima_python.tacvf import artfimaTACVF
from artfima_python.durbin_levinson import DLLoglikelihood
from artfima_python.utils import PacfToAR, InvertibleQ
import pandas as pd

data_path = Path(__file__).parent / "backend" / "data" / "samples" / "co2_levels.csv"
df = pd.read_csv(data_path)
z = df['co2'].values
z_diff = np.diff(z)
w = z_diff - np.mean(z_diff)
n = len(w)

def test_entropy(beta, name):
    print(f"\n{name}:")
    d = beta[0]
    lambda_param = beta[1]

    # Check PACF bounds
    if np.any(np.abs(beta[glpAdd:]) >= 1.0):
        print(f"  ERROR: PACF values out of bounds!")
        return None

    try:
        phi = PacfToAR(beta[glpAdd:(p + glpAdd)])
        theta = PacfToAR(beta[(p + glpAdd):])
    except Exception as e:
        print(f"  ERROR: PacfToAR failed: {e}")
        return None

    if not InvertibleQ(phi) or not InvertibleQ(theta):
        print(f"  ERROR: Not invertible")
        return None

    try:
        r = artfimaTACVF(d=d, lambda_param=lambda_param, phi=phi, theta=theta, maxlag=n-1)
        if not np.all(np.isfinite(r)) or r[0] <= 0:
            print(f"  ERROR: TACVF invalid")
            return None
        ll = DLLoglikelihood(r, w)
        if not np.isfinite(ll):
            print(f"  ERROR: LL not finite")
            return None
        print(f"  d={d:.4f}, lambda={lambda_param:.4f}")
        print(f"  LL={ll:.4f}, negLL={-ll:.4f}")
        return -ll
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

test_entropy(init_low, "low_d")
test_entropy(init_r, "r_like")
