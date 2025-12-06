"""Debug the Entropy function at boundary values"""
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
w = z_diff - np.mean(z_diff)
n = len(w)

print(f"Data: n={n}")

# Test 1: What Python optimizer found (boundary values)
print("\n=== Test 1: Boundary values (d=10, lambda=3) ===")
d = 10.0
lambda_param = 3.0
phi_pacf = np.array([0.99, 0.999801, -0.99])
theta_pacf = np.array([-0.99] * 11)  # Simplified

print(f"phi_pacf: {phi_pacf}")
print(f"theta_pacf: {theta_pacf}")

try:
    phi = PacfToAR(phi_pacf)
    theta = PacfToAR(theta_pacf)
    print(f"phi (AR): {phi}")
    print(f"theta (MA): {theta}")
except Exception as e:
    print(f"PacfToAR error: {e}")
    phi = np.array([])
    theta = np.array([])

try:
    r = artfimaTACVF(d=d, lambda_param=lambda_param, phi=phi, theta=theta, maxlag=n-1)
    print(f"TACVF[0:5]: {r[:5]}")
    print(f"TACVF has NaN: {np.any(np.isnan(r))}")
    print(f"TACVF has Inf: {np.any(np.isinf(r))}")
    print(f"r[0] (variance): {r[0]}")

    if r[0] > 0 and np.all(np.isfinite(r)):
        ll = DLLoglikelihood(r, w)
        negLL = -ll
        print(f"DLLoglikelihood: {ll}")
        print(f"negLL: {negLL}")
        print(f"negLL > 0: {negLL > 0}")
    else:
        print("Invalid TACVF - would return penalty")
except Exception as e:
    print(f"Error: {e}")

# Test 2: R's optimal values
print("\n=== Test 2: R's optimal values ===")
d = 9.999682
lambda_param = 2.021603
phi = np.array([-1.692132, -0.6944333, 0.08887375])
theta = np.array([-0.2645191, 0.7208977, 0.02223315, 0.2195057, 0.5952384,
                  0.1984419, 0.1996436, -0.03327467, -0.1814059, -0.3054669, -0.2574475])

print(f"phi: {phi}")
print(f"theta: {theta}")

try:
    r = artfimaTACVF(d=d, lambda_param=lambda_param, phi=phi, theta=theta, maxlag=n-1)
    print(f"TACVF[0:5]: {r[:5]}")
    print(f"r[0] (variance): {r[0]}")

    if r[0] > 0 and np.all(np.isfinite(r)):
        ll = DLLoglikelihood(r, w)
        negLL = -ll
        print(f"DLLoglikelihood: {ll}")
        print(f"negLL: {negLL}")
        print(f"This should be around 914-915 for LL")
except Exception as e:
    print(f"Error: {e}")

# Test 3: What PACF values lead to R's phi/theta?
print("\n=== Test 3: What PACF gives R's AR/MA? ===")
from artfima_python.utils import ARToPacf

phi_r = np.array([-1.692132, -0.6944333, 0.08887375])
theta_r = np.array([-0.2645191, 0.7208977, 0.02223315, 0.2195057, 0.5952384,
                   0.1984419, 0.1996436, -0.03327467, -0.1814059, -0.3054669, -0.2574475])

try:
    phi_pacf_r = ARToPacf(phi_r)
    theta_pacf_r = ARToPacf(theta_r)
    print(f"phi PACF from R's phi: {phi_pacf_r}")
    print(f"theta PACF from R's theta: {theta_pacf_r}")
    print(f"All phi PACF in (-1,1): {np.all(np.abs(phi_pacf_r) < 1)}")
    print(f"All theta PACF in (-1,1): {np.all(np.abs(theta_pacf_r) < 1)}")
except Exception as e:
    print(f"Error: {e}")
