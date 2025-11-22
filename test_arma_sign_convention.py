"""
Test ARMA sign conventions
"""
import numpy as np
from statsmodels.tsa.arima_process import arma_acovf

print("Testing ARMA sign conventions")
print("=" * 80)

# Test with different sign combinations
test_cases = [
    ("phi=0.5, theta=0.5", -np.array([0.5]), np.array([0.5])),
    ("phi=0.5, theta=-0.5", -np.array([0.5]), np.array([-0.5])),
    ("phi=0.1, theta=0.1", -np.array([0.1]), np.array([0.1])),
    ("phi=0.1, theta=-0.1", -np.array([0.1]), np.array([-0.1])),
]

for name, ar_params, ma_params in test_cases:
    acovf = arma_acovf(ar_params, ma_params, nobs=11, sigma2=1.0)
    print(f"\n{name}:")
    print(f"  ACVF[0:5]: {acovf[:5]}")
    is_wn = np.all(np.abs(acovf[1:]) < 1e-10)
    print(f"  Is white noise: {is_wn}")

# The key insight: In the ARTFIMA optimization, we're estimating partial autocorrelation
# coefficients (PACF), then converting to AR/MA.  But the sign convention might be wrong.

print("\n" + "=" * 80)
print("Understanding ARTFIMA parameter estimation")
print("=" * 80)

# In artfima.py, the parameters are stored as PACF, then converted to AR/MA
# But in tacvfARMA, they're used directly.  This might be the issue.

# Let's check if there's a cancellation when phi = -theta instead of phi = theta
print("\nTesting cancellation conditions:")
for phi in [0.1, 0.5, 0.9]:
    for theta in [phi, -phi]:
        ar_params = -np.array([phi])
        ma_params = np.array([theta])
        acovf = arma_acovf(ar_params, ma_params, nobs=11, sigma2=1.0)
        is_wn = np.all(np.abs(acovf[1:]) < 1e-10)
        print(f"  phi={phi:4.1f}, theta={theta:5.1f}: white noise = {is_wn}, ACVF[1]={acovf[1]:8.4f}")
