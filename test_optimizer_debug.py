"""
Deep debug of the optimizer to understand why it's not moving
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.optimize import minimize

# Add ARTFIMA package to path
artfima_path = Path(__file__).parent / "ARTFIMA"
if str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

# Load data
data_path = Path(__file__).parent / "backend" / "data" / "samples" / "co2_levels.csv"
df = pd.read_csv(data_path)
z = df['co2'].values
z_diff = np.diff(z)

from artfima_python.tacvf import artfimaTACVF
from artfima_python.durbin_levinson import DLLoglikelihood
from artfima_python.utils import PacfToAR, ARToPacf, InvertibleQ

# Setup
p, q = 3, 11
glpAdd = 2  # ARTFIMA
n = len(z_diff)
w = z_diff - np.mean(z_diff)  # Center data
varw = np.var(w)

# Initial values (same as artfima.py)
nbeta = p + q + glpAdd  # = 3 + 11 + 2 = 16
binit = np.zeros(nbeta)
binit[0] = 0.3    # d
binit[1] = 0.025  # lambda
phiInit = ARToPacf(np.tile([0.1, -0.05], (p + 1) // 2)[:p])
binit[glpAdd:(p + glpAdd)] = phiInit
thetaInit = ARToPacf(np.tile([0.7, -0.5], (q + 1) // 2)[:q])
binit[(p + glpAdd):(p + q + glpAdd)] = thetaInit

print(f"Initial parameters (binit):")
print(f"  d={binit[0]}, lambda={binit[1]}")
print(f"  phi PACF: {binit[glpAdd:(p + glpAdd)]}")
print(f"  theta PACF: {binit[(p + glpAdd):(p + q + glpAdd)]}")

# Null model penalty
nullModelLoglikelihood = (-n / 2) * np.log(np.sum(w**2) / n)
entropyPenalty = -nullModelLoglikelihood + 2 * abs(-nullModelLoglikelihood)

print(f"\nNull model LL: {nullModelLoglikelihood:.4f}")
print(f"Entropy penalty: {entropyPenalty:.4f}")

# Bounds
dHi = 10
lambdaLo = 0.000001
lambdaHi = 3
blo = np.concatenate([[-dHi, lambdaLo], np.full(p + q, -0.99)])
bhi = np.concatenate([[dHi, lambdaHi], np.full(p + q, 0.99)])

# Entropy function with debug
call_count = [0]
def Entropy(beta, debug=False):
    call_count[0] += 1

    d = beta[0]
    lambda_param = beta[1]

    if abs(d) > dHi or lambda_param > lambdaHi or lambda_param < lambdaLo:
        if debug:
            print(f"  Call {call_count[0]}: Out of bounds - d={d}, lambda={lambda_param}")
        return entropyPenalty

    # ARMA check
    if np.any(np.abs(beta[glpAdd:(p + q + glpAdd)]) >= 1.0):
        if debug:
            print(f"  Call {call_count[0]}: ARMA coefficients out of range")
        return entropyPenalty

    # Convert PACF to AR/MA
    try:
        phi = PacfToAR(beta[glpAdd:(p + glpAdd)]) if p > 0 else np.array([])
        theta = PacfToAR(beta[(p + glpAdd):(p + q + glpAdd)]) if q > 0 else np.array([])
    except:
        if debug:
            print(f"  Call {call_count[0]}: PACF conversion failed")
        return entropyPenalty

    # Invertibility check
    if (phi.size > 0 and not InvertibleQ(phi)) or (theta.size > 0 and not InvertibleQ(theta)):
        if debug:
            print(f"  Call {call_count[0]}: Not invertible")
        return entropyPenalty

    # Compute likelihood
    try:
        r = artfimaTACVF(d=d, lambda_param=lambda_param, phi=phi, theta=theta, maxlag=n - 1)
        if not np.all(np.isfinite(r)):
            if debug:
                print(f"  Call {call_count[0]}: TACVF not finite")
            return entropyPenalty
        negLL = -DLLoglikelihood(r, w)
        if not np.isfinite(negLL):
            if debug:
                print(f"  Call {call_count[0]}: negLL not finite")
            return entropyPenalty
    except Exception as e:
        if debug:
            print(f"  Call {call_count[0]}: Exception: {e}")
        return entropyPenalty

    if debug:
        print(f"  Call {call_count[0]}: d={d:.4f}, lambda={lambda_param:.4f}, negLL={negLL:.4f}")

    return negLL

# Test 1: Evaluate at initial point
print("\n" + "="*60)
print("TEST: Entropy at initial point")
print("="*60)
f_init = Entropy(binit, debug=True)
print(f"Entropy at binit: {f_init:.4f}")

# Test 2: Compute numerical gradient
print("\n" + "="*60)
print("TEST: Numerical gradient at initial point")
print("="*60)
eps = 1e-8
grad = np.zeros(nbeta)
for i in range(nbeta):
    x_plus = binit.copy()
    x_plus[i] += eps
    x_minus = binit.copy()
    x_minus[i] -= eps
    grad[i] = (Entropy(x_plus) - Entropy(x_minus)) / (2 * eps)

print(f"Gradient at binit:")
print(f"  d_d/d(beta[0]) = {grad[0]:.6f}")
print(f"  d_d/d(beta[1]) = {grad[1]:.6f}")
print(f"  ARMA gradients (first 3): {grad[2:5]}")
print(f"Gradient magnitude: {np.linalg.norm(grad):.6f}")

# Test 3: Check if function changes when moving in gradient direction
print("\n" + "="*60)
print("TEST: Function change in gradient direction")
print("="*60)
for step in [1e-4, 1e-3, 1e-2, 0.1, 0.5, 1.0]:
    x_new = binit - step * grad / np.linalg.norm(grad)
    f_new = Entropy(x_new)
    print(f"  Step {step}: f = {f_new:.4f} (change = {f_new - f_init:.4f})")

# Test 4: Run BFGS with callback to track progress
print("\n" + "="*60)
print("TEST: BFGS optimization with callback")
print("="*60)
call_count[0] = 0
iteration = [0]

def callback(xk):
    iteration[0] += 1
    fk = Entropy(xk)
    print(f"  Iter {iteration[0]}: f={fk:.4f}, d={xk[0]:.4f}, lambda={xk[1]:.4f}")

result = minimize(Entropy, binit, method='BFGS',
                 options={'maxiter': 20, 'disp': True},
                 callback=callback)

print(f"\nBFGS Result:")
print(f"  Success: {result.success}")
print(f"  Message: {result.message}")
print(f"  Function value: {result.fun:.4f}")
print(f"  d={result.x[0]:.4f}, lambda={result.x[1]:.4f}")
print(f"  Number of iterations: {result.nit}")
print(f"  Number of function evaluations: {result.nfev}")
print(f"  Number of gradient evaluations: {result.njev}")

# Test 5: Try L-BFGS-B with bounds
print("\n" + "="*60)
print("TEST: L-BFGS-B optimization with bounds")
print("="*60)
call_count[0] = 0
iteration[0] = 0

result_lbfgsb = minimize(Entropy, binit, method='L-BFGS-B',
                         bounds=list(zip(blo, bhi)),
                         options={'maxiter': 100, 'disp': True},
                         callback=callback)

print(f"\nL-BFGS-B Result:")
print(f"  Success: {result_lbfgsb.success}")
print(f"  Message: {result_lbfgsb.message}")
print(f"  Function value: {result_lbfgsb.fun:.4f}")
print(f"  d={result_lbfgsb.x[0]:.4f}, lambda={result_lbfgsb.x[1]:.4f}")
print(f"  Number of iterations: {result_lbfgsb.nit}")
