"""
Test script to debug ARTFIMA issues with CO2 data
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Add ARTFIMA to path
artfima_path = Path(__file__).parent / "ARTFIMA"
if str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

from artfima_python import artfima as artfima_fit

# Load CO2 data
co2_path = Path(__file__).parent / "backend" / "data" / "samples" / "co2_levels.csv"
df = pd.read_csv(co2_path)
df['date'] = pd.to_datetime(df['date'])
df = df.set_index('date')
z = df['co2'].values

print("=" * 80)
print("CO2 DATA ANALYSIS")
print("=" * 80)
print(f"Data shape: {z.shape}")
print(f"Data range: [{z.min():.2f}, {z.max():.2f}]")
print(f"Data mean: {z.mean():.2f}")
print(f"Data std: {z.std():.2f}")
print(f"First 10 values: {z[:10]}")
print(f"Last 10 values: {z[-10:]}")

print("\n" + "=" * 80)
print("FITTING ARTFIMA(1,d,1) MODEL")
print("=" * 80)

# Fit ARTFIMA model
result = artfima_fit(
    z=z,
    glp="ARTFIMA",
    arimaOrder=(1, 0, 1),  # p=1, D=0, q=1
    likAlg="exact",
    fixd=None,
    b0=None,
    lambdaMax=3,
    dMax=10
)

print(f"\nModel convergence: {result.convergence}")
print(f"d estimate: {result.dHat}")
print(f"lambda estimate: {result.lambdaHat}")
print(f"phi estimate: {result.phiHat}")
print(f"theta estimate: {result.thetaHat}")
print(f"sigmaSq: {result.sigmaSq}")
print(f"Log-likelihood: {result.LL}")
print(f"AIC: {result.aic}")
print(f"BIC: {result.bic}")

print("\n" + "=" * 80)
print("CHECKING TACVF")
print("=" * 80)

from artfima_python.tacvf import artfimaTACVF

# Get parameters
d_val = float(result.dHat) if isinstance(result.dHat, (int, float, np.number)) else 0.0
lambda_val = float(result.lambdaHat) if isinstance(result.lambdaHat, (int, float, np.number)) else 0.0
phi_val = result.phiHat if (result.phiHat is not None and len(result.phiHat) > 0) else np.array([])
theta_val = result.thetaHat if (result.thetaHat is not None and len(result.thetaHat) > 0) else np.array([])

print(f"Computing TACVF with:")
print(f"  d = {d_val}")
print(f"  lambda = {lambda_val}")
print(f"  phi = {phi_val}")
print(f"  theta = {theta_val}")
print(f"  sigma2 = {result.sigmaSq}")

tacvf = artfimaTACVF(
    d=d_val,
    lambda_param=lambda_val,
    phi=phi_val,
    theta=theta_val,
    maxlag=20,
    sigma2=result.sigmaSq
)

print(f"\nTACVF[0:10]: {tacvf[:10]}")
print(f"TACVF range: [{tacvf.min():.6e}, {tacvf.max():.6e}]")
print(f"Any NaN in TACVF: {np.any(np.isnan(tacvf))}")
print(f"Any Inf in TACVF: {np.any(np.isinf(tacvf))}")

print("\n" + "=" * 80)
print("CHECKING EXACT LOG-LIKELIHOOD")
print("=" * 80)

from artfima_python.durbin_levinson import exactLoglikelihood

# Compute on original data
z_centered = z - result.constant
n = len(z_centered)
tacvf_full = artfimaTACVF(
    d=d_val,
    lambda_param=lambda_val,
    phi=phi_val,
    theta=theta_val,
    maxlag=n-1,
    sigma2=result.sigmaSq
)

print(f"Length of TACVF: {len(tacvf_full)}")
print(f"Length of z_centered: {len(z_centered)}")
print(f"z_centered range: [{z_centered.min():.2f}, {z_centered.max():.2f}]")
print(f"z_centered mean: {z_centered.mean():.6f}")

# Check for issues in TACVF
print(f"\nTACVF diagnostics:")
print(f"  TACVF[0] (variance): {tacvf_full[0]:.6e}")
print(f"  Any negative in TACVF: {np.any(tacvf_full < 0)}")
print(f"  Any NaN in TACVF: {np.any(np.isnan(tacvf_full))}")
print(f"  Any Inf in TACVF: {np.any(np.isinf(tacvf_full))}")

if tacvf_full[0] > 0:
    autocorr = tacvf_full / tacvf_full[0]
    print(f"  First 10 autocorrelations: {autocorr[:10]}")

# Compute exact log-likelihood
try:
    ll_result = exactLoglikelihood(tacvf_full, z_centered)
    print(f"\nExact log-likelihood: {ll_result['LL']}")
    print(f"Estimated sigmaSq: {ll_result['sigmaSq']}")

    # Compare with reported LL
    print(f"\nReported LL: {result.LL}")
    print(f"Difference: {abs(result.LL - ll_result['LL'])}")

    # Check AIC/BIC computation
    K = result.nbeta
    n = len(z_centered)
    aic_manual = (-2) * ll_result['LL'] + 2 * (K + 2)
    bic_manual = (-2) * ll_result['LL'] + (K + 2) * np.log(n)

    print(f"\nManual AIC computation:")
    print(f"  K (nbeta): {K}")
    print(f"  n: {n}")
    print(f"  -2*LL: {-2 * ll_result['LL']}")
    print(f"  2*(K+2): {2 * (K + 2)}")
    print(f"  AIC = {aic_manual}")
    print(f"  Reported AIC = {result.aic}")

    print(f"\nManual BIC computation:")
    print(f"  (K+2)*log(n): {(K + 2) * np.log(n)}")
    print(f"  BIC = {bic_manual}")
    print(f"  Reported BIC = {result.bic}")

except Exception as e:
    print(f"ERROR computing exact log-likelihood: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TESTING FORECAST")
print("=" * 80)

try:
    forecast_result = result.forecast(n_ahead=12)
    forecasts = forecast_result['Forecasts']
    forecast_sd = forecast_result['SDForecasts']

    print(f"Forecasts: {forecasts}")
    print(f"Forecast SD: {forecast_sd}")
    print(f"Forecast range: [{forecasts.min():.2f}, {forecasts.max():.2f}]")
    print(f"Last actual value: {z[-1]:.2f}")
    print(f"Difference from last value: {forecasts[0] - z[-1]:.2f}")

except Exception as e:
    print(f"ERROR in forecast: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("DONE")
print("=" * 80)
