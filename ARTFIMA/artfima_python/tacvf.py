"""
Theoretical Autocovariance Function (TACVF) for ARTFIMA models

This module implements the theoretical autocovariance functions for:
- ARTFIMA (Autoregressive Tempered Fractionally Integrated Moving Average)
- ARFIMA (Autoregressive Fractionally Integrated Moving Average)
- ARMA (Autoregressive Moving Average)
"""

import numpy as np
from scipy.special import gamma, hyp2f1, gammaln
from scipy.fft import fft, ifft


def tacvfFDWN(dfrac, maxlag, sigma2=1.0):
    """
    Autocovariance function for fractionally differenced white noise (FDWN).
    
    Parameters:
    -----------
    dfrac : float
        Fractional differencing parameter, must be < 0.5
    maxlag : int
        Maximum lag for autocovariance
    sigma2 : float, default=1.0
        Innovation variance
        
    Returns:
    --------
    numpy.ndarray
        Autocovariance function from lag 0 to maxlag
    """
    if dfrac > 0.499:
        dfrac = 0.499
    x = np.zeros(maxlag + 1)
    x[0] = gamma(1 - 2 * dfrac) / (gamma(1 - dfrac) ** 2)
    for i in range(1, maxlag + 1):
        x[i] = ((i - 1 + dfrac) / (i - dfrac)) * x[i - 1]
    return x * sigma2


def tacvfFI(d, lambda_param, maxlag, sigma2=1.0):
    """
    Autocovariance function for tempered fractional integration (TFI).
    
    Parameters:
    -----------
    d : float
        Fractional differencing parameter
    lambda_param : float
        Tempering parameter
    maxlag : int
        Maximum lag for autocovariance
    sigma2 : float, default=1.0
        Innovation variance
        
    Returns:
    --------
    numpy.ndarray
        Autocovariance function from lag 0 to maxlag
    """
    if abs(d) < 1e-8:
        return np.concatenate([[sigma2], np.zeros(maxlag)])
    
    k = np.arange(maxlag + 1)
    
    if d > 0:
        exL = min(np.exp(-2 * lambda_param), 0.99)
        # Hypergeometric function 2F1
        A = hyp2f1(d, d + k, 1 + k, exL)
        
        # Check for NaN
        if np.any(np.isnan(A)):
            raise ValueError("NaN from hyp2f1() in tacvfFI()")
        
        # lnpoch(d, k) = ln(gamma(d + k) / gamma(d))
        B = gammaln(d + k) - gammaln(d)
        C = k * lambda_param + gammaln(1 + k)
        ans = A * np.exp(B - C)
    else:
        # Approximation when d < 0
        ans = np.exp(-lambda_param * k) * tacvfFDWN(max(d, -0.499), maxlag)
    
    return sigma2 * ans


def tacvfARMA(phi=None, theta=None, maxlag=20, sigma2=1.0):
    """
    Autocovariance function for ARMA model.

    Uses statsmodels' robust implementation to avoid numerical issues
    when AR and MA coefficients are similar.

    Parameters:
    -----------
    phi : array-like, optional
        AR coefficients
    theta : array-like, optional
        MA coefficients
    maxlag : int, default=20
        Maximum lag for autocovariance
    sigma2 : float, default=1.0
        Innovation variance

    Returns:
    --------
    numpy.ndarray
        Autocovariance function from lag 0 to maxlag
    """
    if phi is None:
        phi = np.array([])
    else:
        phi = np.asarray(phi).flatten()
    if theta is None:
        theta = np.array([])
    else:
        theta = np.asarray(theta).flatten()

    p = len(phi)
    q = len(theta)

    # White noise case
    if max(p, q) == 0:
        return np.concatenate([[sigma2], np.zeros(maxlag)])

    # Use original implementation (statsmodels has issues with ARMA ACVF computation)
    r = max(p, q) + 1
    b = np.zeros(r)
    C = np.zeros(q + 1)
    C[0] = 1
    theta2 = np.concatenate([[-1], theta])
    phi2 = np.zeros(3 * r)
    phi2[r - 1] = -1

    if p > 0:
        phi2[r:r + p] = phi

    if q > 0:
        for k in range(1, q + 1):
            C[k] = -theta[k - 1]
            if p > 0:
                for i in range(1, min(p, k) + 1):
                    C[k] = C[k] + phi[i - 1] * C[k - i]

    for k in range(q + 1):
        for i in range(k, q + 1):
            b[k] = b[k] - theta2[i] * C[i - k]

    if p == 0:
        g = np.concatenate([b, np.zeros(maxlag+1)])[:maxlag+1]
        return g * sigma2
    else:
        a = np.zeros((r, r))
        for i in range(r):
            for j in range(r):
                if j == 0:
                    a[i, j] = phi2[r + i - 1]
                else:
                    a[i, j] = phi2[r + i - j - 1] + phi2[r + i + j - 1]

        g = np.linalg.solve(a, -b)
        if len(g) <= maxlag:
            g = np.concatenate([g, np.zeros(maxlag+1 - r)])
            for i in range(r, maxlag+1):
                g[i] = np.dot(phi, g[i - 1:i - p - 1:-1])
            return g[:maxlag+1] * sigma2
        else:
            return g[:maxlag+1] * sigma2


def symtacvf(x):
    """
    Create symmetric autocovariance function for convolution.

    R implementation: c(rev(x[-1])[-1], x)
    - x[-1] removes first element
    - rev() reverses
    - [-1] removes first element of reversed
    - Result: [x[n-1], x[n-2], ..., x[2], x[0], x[1], ..., x[n]]

    Parameters:
    -----------
    x : array-like
        Autocovariance function from lag 0

    Returns:
    --------
    numpy.ndarray
        Symmetric autocovariance function
    """
    x = np.asarray(x)
    # x[1:] removes first element, [::-1] reverses, [1:] removes first of reversed
    # Equivalent to R's rev(x[-1])[-1]
    reversed_without_first_twice = x[1:][::-1][1:]
    return np.concatenate([reversed_without_first_twice, x])


def mix(x, y):
    """
    Mix two autocovariance functions using FFT convolution.

    Computes the convolution of two TACVF functions in the frequency domain.
    This is a direct translation of the R implementation.

    R version: rev(Re(fft(fft(symtacvf(x)) * fft(symtacvf(y)), inverse = TRUE)/n)[(n/2 - 1):(n - 1)])

    Note: R's fft(x, inverse=TRUE)/n is equivalent to Python's ifft(x) (already normalized)

    Parameters:
    -----------
    x : array-like
        First autocovariance function
    y : array-like
        Second autocovariance function

    Returns:
    --------
    numpy.ndarray
        Mixed autocovariance function
    """
    x = np.asarray(x)
    y = np.asarray(y)
    n = 2 * len(x) - 2
    # Create symmetric versions for FFT
    sx = symtacvf(x)
    sy = symtacvf(y)
    # Convolve in frequency domain: FFT, multiply, inverse FFT
    # ifft() in Python is already normalized (equivalent to R's fft(..., inverse=TRUE)/n)
    result = np.real(ifft(fft(sx) * fft(sy)))
    # Extract indices (n/2 - 1):(n - 1) and reverse
    # R uses 1-based indexing: (n/2 - 1):(n - 1)
    # R's index 19:39 (1-based) = Python's index 18:39 (0-based, end exclusive)
    # So: (n//2 - 1 - 1):(n - 1) = (n//2 - 2):(n - 1)
    extracted = result[(n // 2 - 2):(n - 1)]
    # Reverse to match R's rev() function
    return extracted[::-1]


def artfimaTACVF(d=None, lambda_param=None, phi=None, theta=None, maxlag=None, 
                  sigma2=1.0, obj=None):
    """
    Theoretical autocovariance function for ARTFIMA model.
    
    Parameters:
    -----------
    d : float, optional
        Fractional differencing parameter
    lambda_param : float, optional
        Tempering parameter
    phi : array-like, optional
        AR coefficients
    theta : array-like, optional
        MA coefficients
    maxlag : int
        Maximum lag for autocovariance
    sigma2 : float, default=1.0
        Innovation variance
    obj : object, optional
        ARTFIMA model object with dHat, lambdaHat, phiHat, thetaHat, sigmaSq
        
    Returns:
    --------
    numpy.ndarray
        Autocovariance function from lag 0 to maxlag
    """
    if obj is not None:
        if hasattr(obj, 'dHat'):
            d = obj.dHat
            lambda_param = obj.lambdaHat
            phi = obj.phiHat
            theta = obj.thetaHat
            sigma2 = obj.sigmaSq
    
    # Handle d parameter - keep as scalar for computation
    if d is None:
        d = None
        d_val = None
    else:
        d = np.asarray(d)
        # Extract scalar value if it's a 0-d array or 1-element array
        if d.ndim == 0:
            d_val = float(d.item())
        elif d.size == 1:
            d_val = float(d.flat[0])
        elif d.size == 0:
            d_val = None
        else:
            # Multiple values - use first one (shouldn't happen in normal use)
            d_val = float(d.flat[0])

    # Handle lambda_param parameter - keep as scalar for computation
    if lambda_param is None:
        lambda_param = None
        lambda_val = None
    else:
        lambda_param = np.asarray(lambda_param)
        # Extract scalar value if it's a 0-d array or 1-element array
        if lambda_param.ndim == 0:
            lambda_val = float(lambda_param.item())
        elif lambda_param.size == 1:
            lambda_val = float(lambda_param.flat[0])
        elif lambda_param.size == 0:
            lambda_val = None
        else:
            # Multiple values - use first one (shouldn't happen in normal use)
            lambda_val = float(lambda_param.flat[0])
    
    if phi is None:
        phi = np.array([])
    else:
        phi = np.asarray(phi)
    if theta is None:
        theta = np.array([])
    else:
        theta = np.asarray(theta)

    ARMALength = len(phi) + len(theta)
    # Check if we have fractional parameters
    has_d = (d_val is not None)
    has_lambda = (lambda_val is not None)
    ARTFIMALength = ARMALength + (1 if has_d else 0) + (1 if has_lambda else 0)

    # White noise case
    if ARTFIMALength == 0:
        return np.concatenate([[sigma2], np.zeros(maxlag)])

    # Pure ARMA case (no fractional differencing or d ≈ 0)
    isARMA = (not has_d) or (has_d and abs(d_val) < 1e-10)
    if isARMA:
        return tacvfARMA(phi=phi, theta=theta, maxlag=maxlag, sigma2=sigma2)

    # Fractional case
    lagTrunc = 2 * max(128, 2 ** int(np.ceil(np.log2(maxlag))))

    # Use tempered FI if lambda is significant, otherwise use standard FI
    if has_lambda and lambda_val > 1e-7:
        x = tacvfFI(d=d_val, lambda_param=lambda_val, maxlag=lagTrunc)
    else:
        # Use standard fractional differencing
        x = tacvfFDWN(dfrac=d_val, maxlag=lagTrunc)

    if ARMALength == 0:
        return sigma2 * x[:(maxlag + 1)]

    # ARMA case - combine fractional and ARMA components
    y = tacvfARMA(phi=phi, theta=theta, maxlag=lagTrunc, sigma2=1.0)
    z = sigma2 * mix(x, y)
    return z[:(maxlag + 1)]

