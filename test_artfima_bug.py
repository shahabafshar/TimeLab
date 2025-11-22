"""
Focused test to find the exact bug in ARTFIMA
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Add ARTFIMA to path
artfima_path = Path(__file__).parent / "ARTFIMA"
if str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

from artfima_python.tacvf import artfimaTACVF
from artfima_python.durbin_levinson import exactLoglikelihood

# Load CO2 data
co2_path = Path(__file__).parent / "backend" / "data" / "samples" / "co2_levels.csv"
df = pd.read_csv(co2_path)
z = df['co2'].values

# Simulate what artfima.py does
w = z.copy()
mnw = np.mean(w)
w = w - mnw
n = len(w)

print("=" * 80)
print("TESTING TACVF AND LOG-LIKELIHOOD COMPUTATION")
print("=" * 80)
print(f"n = {n}")
print(f"w mean (should be ~0): {np.mean(w):.6f}")
print(f"w std: {np.std(w):.6f}")

# Use fixed parameters from the fitted model
d_val = 0.3
lambda_val = 0.025
phi_val = np.array([0.1])
theta_val = np.array([0.1])

print(f"\nParameters:")
print(f"  d = {d_val}")
print(f"  lambda = {lambda_val}")
print(f"  phi = {phi_val}")
print(f"  theta = {theta_val}")

# Compute TACVF with sigma2=1.0 (as artfima.py does at line 543-544)
print(f"\n" + "-" * 80)
print("Computing TACVF with sigma2=1.0 (default)")
print("-" * 80)

rHat = artfimaTACVF(
    d=d_val,
    lambda_param=lambda_val,
    phi=phi_val,
    theta=theta_val,
    maxlag=n - 1
    # NOTE: sigma2 is NOT passed, so defaults to 1.0
)

print(f"rHat length: {len(rHat)}")
print(f"rHat[0] (should be close to 1.0): {rHat[0]:.6f}")
print(f"rHat[0:10]: {rHat[:10]}")
print(f"Any NaN in rHat: {np.any(np.isnan(rHat))}")
print(f"Any Inf in rHat: {np.any(np.isinf(rHat))}")
print(f"Any negative in rHat: {np.any(rHat < 0)}")
print(f"rHat range: [{rHat.min():.6f}, {rHat.max():.6f}]")

# Compute exact log-likelihood
print(f"\n" + "-" * 80)
print("Computing exact log-likelihood")
print("-" * 80)

ansEx = exactLoglikelihood(rHat, w)
LL = ansEx['LL']
sigmaSq = ansEx['sigmaSq']

print(f"Log-likelihood: {LL}")
print(f"sigmaSq: {sigmaSq}")

# Check if sigmaSq is reasonable
print(f"\nExpected sigmaSq (close to var(w)): {np.var(w):.6f}")
print(f"Is sigmaSq positive: {sigmaSq > 0}")
print(f"Is sigmaSq finite: {np.isfinite(sigmaSq)}")

# Compute AIC/BIC
nbeta = 4  # For ARTFIMA(1,d,1): d, lambda, phi[0] (as pacf), theta[0] (as pacf)
aic = (-2) * LL + 2 * (nbeta + 2)
bic = (-2) * LL + (nbeta + 2) * np.log(n)

print(f"\nAIC: {aic}")
print(f"BIC: {bic}")

# Now let's check what happens in the reported model
print(f"\n" + "=" * 80)
print("WHAT THE FITTED MODEL REPORTS (FROM DEBUG SCRIPT)")
print("=" * 80)
print(f"Reported sigmaSq: -1.8817290968064087e+22")
print(f"Reported LL: 7.432829932385314e+24")
print(f"Reported AIC: -1.4865659864770629e+25")
print(f"Reported BIC: -1.4865659864770629e+25")

print(f"\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print(f"The bug is that the reported values are incorrect.")
print(f"Expected LL: {LL:.2f}, Got: 7.43e24")
print(f"Expected sigmaSq: {sigmaSq:.6f}, Got: -1.88e22")
print(f"Expected AIC: {aic:.2f}, Got: -1.49e25")

# Check artfima.py line 579-585 more carefully
print(f"\n" + "=" * 80)
print("CHECKING ARTFIMA.PY CODE")
print("=" * 80)
print("artfima.py line 543-544:")
print("  rHat = artfimaTACVF(d=d_val, lambda_param=lambda_val, phi=phi_val,")
print("                      theta=theta_val, maxlag=n - 1)")
print("  NOTE: sigma2 is NOT passed, defaults to 1.0 ✓")
print("")
print("artfima.py line 579-585:")
print("  try:")
print("      ansEx = exactLoglikelihood(rHat, w)")
print("      LL = ansEx['LL']")
print("      sigmaSq = ansEx['sigmaSq']")
print("  except:")
print("      LL = np.nan")
print("      sigmaSq = np.nan")
print("")
print("This should work correctly. Let's check the result object...")
