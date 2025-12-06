"""
Verify Python ARTFIMA implementation against theoretical formulas from:
"Parameter estimation for ARTFIMA time series"
by Sabzikar, McLeod, and Meerschaert

Key equation (Eq. 1125 in the paper):
gamma_W(k) = sigma^2 * exp(-lambda*k) * Gamma(k+d) / (Gamma(d)*Gamma(k+1)) * 2F1(d, k+d, k+1, exp(-2*lambda))

This script verifies that our Python implementation correctly computes this formula.
"""
import sys
import numpy as np
from scipy.special import gamma, gammaln, hyp2f1
from pathlib import Path

# Add ARTFIMA to path
artfima_path = Path(__file__).parent / "ARTFIMA"
if str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

from artfima_python.tacvf import tacvfFI, tacvfFDWN, tacvfARMA, mix, artfimaTACVF

print("=" * 80)
print("VERIFICATION AGAINST THEORETICAL PAPER FORMULAS")
print("=" * 80)

# Test 1: Verify tacvfFI matches equation (1125)
print("\n1. Verifying tacvfFI against Equation (1125) from paper")
print("-" * 80)

def theoretical_tacvfFI(d, lambda_param, k, sigma2=1.0):
    """
    Direct implementation of Equation (1125):
    gamma_W(k) = sigma^2 * exp(-lambda*k) * Gamma(k+d) / (Gamma(d)*Gamma(k+1)) * 2F1(d, k+d, k+1, exp(-2*lambda))
    """
    exL = np.exp(-2 * lambda_param)
    # Hypergeometric function: 2F1(d, k+d, k+1, exp(-2*lambda))
    A = hyp2f1(d, d + k, 1 + k, exL)
    # Gamma ratio: Gamma(k+d) / (Gamma(d) * Gamma(k+1))
    if isinstance(k, np.ndarray):
        # For numerical stability, use log-gamma
        log_gamma_ratio = gammaln(k + d) - gammaln(d) - gammaln(k + 1)
        gamma_ratio = np.exp(log_gamma_ratio)
    else:
        gamma_ratio = gamma(k + d) / (gamma(d) * gamma(k + 1))
    # Exponential term: exp(-lambda * k)
    exp_term = np.exp(-lambda_param * k)
    return sigma2 * exp_term * gamma_ratio * A

d = 0.3
lambda_param = 0.025
maxlag = 20
sigma2 = 1.0

# Our implementation
our_result = tacvfFI(d=d, lambda_param=lambda_param, maxlag=maxlag, sigma2=sigma2)

# Theoretical formula
k = np.arange(maxlag + 1)
theoretical_result = theoretical_tacvfFI(d, lambda_param, k, sigma2)

print(f"   Parameters: d={d}, lambda={lambda_param}")
print(f"   Our tacvfFI[0:5]:         {our_result[:5]}")
print(f"   Theoretical formula[0:5]: {theoretical_result[:5]}")
print(f"   Max absolute error:       {np.max(np.abs(our_result - theoretical_result)):.2e}")
print(f"   Match: {np.allclose(our_result, theoretical_result)}")

# Test 2: Verify tacvfFDWN for the limiting case (lambda -> 0)
print("\n2. Verifying tacvfFDWN (ARFIMA case, no tempering)")
print("-" * 80)

def theoretical_tacvfFDWN(d, k, sigma2=1.0):
    """
    Theoretical ACVF for fractionally differenced white noise.
    gamma(k) = sigma^2 * Gamma(1-2d) / Gamma(1-d)^2 * prod_{j=1}^{k} (j-1+d)/(j-d)
    """
    if d > 0.499:
        d = 0.499
    x = np.zeros(len(k) if isinstance(k, np.ndarray) else 1)
    x[0] = sigma2 * gamma(1 - 2*d) / (gamma(1 - d)**2)
    for i in range(1, len(k) if isinstance(k, np.ndarray) else 1):
        x[i] = ((i - 1 + d) / (i - d)) * x[i-1]
    return x

d = 0.3
maxlag = 20

our_fdwn = tacvfFDWN(dfrac=d, maxlag=maxlag, sigma2=1.0)
k = np.arange(maxlag + 1)
theoretical_fdwn = theoretical_tacvfFDWN(d, k, sigma2=1.0)

print(f"   Parameters: d={d}")
print(f"   Our tacvfFDWN[0:5]:       {our_fdwn[:5]}")
print(f"   Theoretical formula[0:5]: {theoretical_fdwn[:5]}")
print(f"   Max absolute error:       {np.max(np.abs(our_fdwn - theoretical_fdwn)):.2e}")
print(f"   Match: {np.allclose(our_fdwn, theoretical_fdwn)}")

# Test 3: Verify ARMA autocovariance (Yule-Walker equations)
print("\n3. Verifying tacvfARMA (Yule-Walker equations)")
print("-" * 80)

# For AR(1) with phi, the theoretical ACVF is:
# gamma(0) = sigma^2 / (1 - phi^2)
# gamma(k) = phi^k * gamma(0)

phi = np.array([0.7])
maxlag = 10
sigma2 = 1.0

our_arma = tacvfARMA(phi=phi, theta=np.array([]), maxlag=maxlag, sigma2=sigma2)

# Theoretical AR(1) ACVF
gamma0_theoretical = sigma2 / (1 - phi[0]**2)
theoretical_ar1 = np.array([gamma0_theoretical * phi[0]**k for k in range(maxlag+1)])

print(f"   AR(1) with phi={phi[0]}")
print(f"   Our tacvfARMA[0:5]:       {our_arma[:5]}")
print(f"   Theoretical AR(1)[0:5]:   {theoretical_ar1[:5]}")
print(f"   Max absolute error:       {np.max(np.abs(our_arma - theoretical_ar1)):.2e}")
print(f"   Match: {np.allclose(our_arma, theoretical_ar1)}")

# Test 4: Verify MA(1) autocovariance
print("\n4. Verifying MA(1) autocovariance")
print("-" * 80)

# For MA(1) with theta, the theoretical ACVF is:
# gamma(0) = sigma^2 * (1 + theta^2)
# gamma(1) = -sigma^2 * theta
# gamma(k) = 0 for k >= 2

theta = np.array([0.5])
maxlag = 10
sigma2 = 1.0

our_ma = tacvfARMA(phi=np.array([]), theta=theta, maxlag=maxlag, sigma2=sigma2)

# Theoretical MA(1) ACVF
gamma0_ma = sigma2 * (1 + theta[0]**2)
gamma1_ma = -sigma2 * theta[0]
theoretical_ma1 = np.zeros(maxlag + 1)
theoretical_ma1[0] = gamma0_ma
theoretical_ma1[1] = gamma1_ma

print(f"   MA(1) with theta={theta[0]}")
print(f"   Our tacvfARMA[0:5]:       {our_ma[:5]}")
print(f"   Theoretical MA(1)[0:5]:   {theoretical_ma1[:5]}")
print(f"   Max absolute error:       {np.max(np.abs(our_ma - theoretical_ma1)):.2e}")
print(f"   Match: {np.allclose(our_ma, theoretical_ma1)}")

# Test 5: Verify mix() is performing convolution correctly
print("\n5. Verifying mix() function (FFT convolution)")
print("-" * 80)

# Property: mix(x, delta) = x where delta = [1, 0, 0, ...]
x = tacvfFDWN(dfrac=0.3, maxlag=20, sigma2=1.0)
delta = np.zeros(21)
delta[0] = 1.0

result_mix = mix(x, delta)
print(f"   Input x[0:5]: {x[:5]}")
print(f"   Delta (unit impulse): [1, 0, 0, ...]")
print(f"   mix(x, delta)[0:5]: {result_mix[:5]}")
print(f"   Match x: {np.allclose(result_mix, x)}")

# Test 6: Verify full ARTFIMA TACVF
print("\n6. Verifying full artfimaTACVF")
print("-" * 80)

# With d=0, lambda=0, should reduce to pure ARMA
d = 0.0
lambda_param = 0.0
phi = np.array([0.5])
theta = np.array([0.3])
maxlag = 20

artfima_result = artfimaTACVF(d=d, lambda_param=lambda_param, phi=phi, theta=theta, maxlag=maxlag, sigma2=1.0)
arma_result = tacvfARMA(phi=phi, theta=theta, maxlag=maxlag, sigma2=1.0)

print(f"   Parameters: d={d}, lambda={lambda_param}, phi={phi}, theta={theta}")
print(f"   artfimaTACVF[0:5]:        {artfima_result[:5]}")
print(f"   tacvfARMA[0:5]:           {arma_result[:5]}")
print(f"   Match (d=0 reduces to ARMA): {np.allclose(artfima_result, arma_result)}")

# Test 7: Verify ARTFIMA vs ARFIMA difference
print("\n7. Comparing ARTFIMA vs ARFIMA (effect of tempering)")
print("-" * 80)

d = 0.3
maxlag = 50

# ARFIMA (no tempering)
arfima_acvf = tacvfFDWN(dfrac=d, maxlag=maxlag, sigma2=1.0)

# ARTFIMA (with tempering)
artfima_acvf = tacvfFI(d=d, lambda_param=0.05, maxlag=maxlag, sigma2=1.0)

print(f"   d={d}, comparing lambda=0 (ARFIMA) vs lambda=0.05 (ARTFIMA)")
print(f"   ARFIMA acvf[40:51]:  {arfima_acvf[40:51]}")
print(f"   ARTFIMA acvf[40:51]: {artfima_acvf[40:51]}")
print(f"   Note: ARTFIMA decays exponentially faster than ARFIMA (as expected from theory)")

# Summary
print("\n" + "=" * 80)
print("VERIFICATION SUMMARY")
print("=" * 80)

tests = [
    ("tacvfFI vs Eq. 1125", np.allclose(our_result, theoretical_result)),
    ("tacvfFDWN formula", np.allclose(our_fdwn, theoretical_fdwn)),
    ("tacvfARMA AR(1)", np.allclose(our_arma, theoretical_ar1)),
    ("tacvfARMA MA(1)", np.allclose(our_ma, theoretical_ma1)),
    ("mix() identity", np.allclose(result_mix, x)),
    ("artfimaTACVF d=0", np.allclose(artfima_result, arma_result)),
]

all_passed = True
for name, passed in tests:
    status = "[OK]" if passed else "[FAIL]"
    print(f"   {name}: {status}")
    all_passed = all_passed and passed

if all_passed:
    print("\n[OK] ALL THEORETICAL VERIFICATION TESTS PASSED!")
    print("     Python implementation correctly implements the ARTFIMA formulas")
    print("     from Sabzikar, McLeod & Meerschaert (2016)")
else:
    print("\n[FAIL] Some verification tests failed - review implementation")
