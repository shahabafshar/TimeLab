"""
Systematically test what ARMA combinations produce white noise
"""
import numpy as np
from statsmodels.tsa.arima_process import arma_acovf

print("Testing ARMA combinations for white noise")
print("=" * 80)

phi_values = [0.1, 0.3, 0.5, 0.7, 0.9]
theta_values = [0.1, 0.3, 0.5, 0.7, 0.9]

white_noise_cases = []
good_cases = []

for phi in phi_values:
    for theta in theta_values:
        ar_params = -np.array([phi])
        ma_params = np.array([theta])

        acovf = arma_acovf(ar_params, ma_params, nobs=11, sigma2=1.0)
        is_wn = np.all(np.abs(acovf[1:]) < 1e-10)

        if is_wn:
            white_noise_cases.append((phi, theta))
        else:
            good_cases.append((phi, theta, acovf[1]))

print(f"\nWhite noise cases (phi, theta):")
for phi, theta in white_noise_cases:
    print(f"  phi={phi:.1f}, theta={theta:.1f}")

print(f"\nGood cases (phi, theta, acovf[1]):")
for phi, theta, ac1 in good_cases:
    print(f"  phi={phi:.1f}, theta={theta:.1f}, acovf[1]={ac1:.4f}")

# Find pattern
print("\n" + "=" * 80)
print("Pattern analysis:")
print("=" * 80)

wn_array = np.array(white_noise_cases)
if len(wn_array) > 0:
    # Check if phi == theta for all WN cases
    all_equal = np.all(np.abs(wn_array[:, 0] - wn_array[:, 1]) < 0.01)
    print(f"All WN cases have phi ≈ theta: {all_equal}")

    if all_equal:
        print(f"\nCONCLUSION: ARMA(1,1) with phi==theta ALWAYS produces white noise!")
        print(f"This is a mathematical property, not a bug.")
        print(f"\nSOLUTION: Use different initial values for phi and theta.")
