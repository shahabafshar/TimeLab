"""
Test statsmodels sign conventions more carefully
"""
import numpy as np
from statsmodels.tsa.arima_process import arma_acovf

print("Testing statsmodels sign conventions")
print("=" * 80)

phi = 0.9
theta = 0.1

# Test different sign combinations
test_cases = [
    ("ar=-phi, ma=+theta", -np.array([phi]), np.array([theta])),
    ("ar=+phi, ma=+theta", np.array([phi]), np.array([theta])),
    ("ar=-phi, ma=-theta", -np.array([phi]), -np.array([theta])),
    ("ar=+phi, ma=-theta", np.array([phi]), -np.array([theta])),
]

for name, ar_params, ma_params in test_cases:
    acovf = arma_acovf(ar_params, ma_params, nobs=11, sigma2=1.0)
    is_wn = np.all(np.abs(acovf[1:]) < 1e-10)
    print(f"\n{name}:")
    print(f"  ACVF[0:5]: {acovf[:5]}")
    print(f"  Is white noise: {is_wn}")
