"""
Test using statsmodels for ARMA ACVF computation
"""
import sys
import numpy as np
from pathlib import Path

# Test if statsmodels has ARMA ACVF function
from statsmodels.tsa.arima_process import arma_acovf

print("Testing statsmodels arma_acovf function")
print("=" * 80)

# Test with phi=0.1, theta=0.1
phi = np.array([0.1])
theta = np.array([0.1])
maxlag = 20
sigma2 = 1.0

print(f"Parameters:")
print(f"  AR: {phi}")
print(f"  MA: {theta}")
print(f"  sigma2: {sigma2}")
print()

# statsmodels uses a different parameterization
# AR polynomial: 1 - phi[0]*L - phi[1]*L^2 - ...
# MA polynomial: 1 + theta[0]*L + theta[1]*L^2 + ...
# So we need to negate AR coefficients
ar_params = -phi  # statsmodels convention
ma_params = theta  # statsmodels convention

print(f"statsmodels AR params (negated): {ar_params}")
print(f"statsmodels MA params: {ma_params}")
print()

# Compute ACVF
acovf = arma_acovf(ar_params, ma_params, nobs=maxlag+1, sigma2=sigma2)
print(f"ACVF length: {len(acovf)}")
print(f"ACVF[0:10]: {acovf[:10]}")
print(f"ACVF range: [{acovf.min():.6f}, {acovf.max():.6f}]")
print()

# Test other cases
print("=" * 80)
print("Testing various ARMA configurations")
print("=" * 80)

test_cases = [
    ("AR(1) phi=0.5", np.array([0.5]), None),
    ("MA(1) theta=0.5", None, np.array([0.5])),
    ("ARMA(1,1) phi=0.5, theta=0.5", np.array([0.5]), np.array([0.5])),
    ("ARMA(1,1) phi=0.1, theta=0.1", np.array([0.1]), np.array([0.1])),
]

for name, phi_test, theta_test in test_cases:
    ar_params = -phi_test if phi_test is not None else np.array([])
    ma_params = theta_test if theta_test is not None else np.array([])

    acovf = arma_acovf(ar_params, ma_params, nobs=11, sigma2=sigma2)
    print(f"\n{name}:")
    print(f"  ACVF[0:5]: {acovf[:5]}")
    print(f"  All zeros (except [0]): {np.all(np.abs(acovf[1:]) < 1e-10)}")
