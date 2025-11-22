"""
Durbin-Levinson algorithm for computing log-likelihood and residuals
for ARTFIMA models.

This implements the exact likelihood computation using the Durbin-Levinson
algorithm, which is more efficient than direct matrix inversion for
Toeplitz covariance matrices.
"""

import numpy as np
from scipy.linalg import solve_toeplitz, toeplitz


def DLLoglikelihood(r, z):
    """
    Compute log-likelihood using Durbin-Levinson algorithm.
    
    Parameters:
    -----------
    r : array-like
        Autocovariance function from lag 0
    z : array-like
        Time series data (centered)
        
    Returns:
    --------
    float
        Log-likelihood value
    """
    r = np.asarray(r)
    z = np.asarray(z)
    n = len(z)
    
    if len(r) < n:
        raise ValueError("Autocovariance function must have at least n elements")
    
    # Initialize
    v = r[0]
    ll = -0.5 * (n * np.log(2 * np.pi) + np.log(v) + z[0]**2 / v)
    
    if n == 1:
        return ll
    
    phi = np.zeros(n - 1)
    v_prev = v
    
    for i in range(1, n):
        # Compute partial autocorrelation
        phi_new = r[i]
        if i > 1:
            phi_new = phi_new - np.dot(phi[:i-1], r[i-1:0:-1])
        phi_new = phi_new / v_prev
        
        # Update variance
        v_new = v_prev * (1 - phi_new**2)
        
        # Update coefficients
        if i > 1:
            phi[:i-1] = phi[:i-1] - phi_new * phi[i-2::-1]
        phi[i-1] = phi_new
        
        # Compute prediction error
        pred = np.dot(phi[:i], z[i-1::-1])
        err = z[i] - pred
        
        # Update log-likelihood
        ll = ll - 0.5 * (np.log(v_new) + err**2 / v_new)
        
        v_prev = v_new
    
    return ll


def DLResiduals(r, z):
    """
    Compute residuals using Durbin-Levinson algorithm.
    
    Parameters:
    -----------
    r : array-like
        Autocovariance function from lag 0
    z : array-like
        Time series data (centered)
        
    Returns:
    --------
    numpy.ndarray
        Residuals
    """
    r = np.asarray(r)
    z = np.asarray(z)
    n = len(z)
    
    if len(r) < n:
        raise ValueError("Autocovariance function must have at least n elements")
    
    # Build Toeplitz matrix
    R = toeplitz(r[:n])
    
    # Solve for residuals: R * residuals = z
    # Using Cholesky decomposition for efficiency
    try:
        L = np.linalg.cholesky(R)
        y = np.linalg.solve(L, z)
        residuals = np.linalg.solve(L.T, y)
    except np.linalg.LinAlgError:
        # Fallback to direct solve if Cholesky fails
        residuals = np.linalg.solve(R, z)
    
    return residuals


def exactLoglikelihood(r, z):
    """
    Compute exact log-likelihood and innovation variance.
    
    Parameters:
    -----------
    r : array-like
        Autocovariance function from lag 0
    z : array-like
        Time series data (centered)
        
    Returns:
    --------
    dict
        Dictionary with keys 'LL' (log-likelihood) and 'sigmaSq' (innovation variance)
    """
    r = np.asarray(r)
    z = np.asarray(z)
    n = len(z)
    
    if len(r) < n:
        raise ValueError("Autocovariance function must have at least n elements")
    
    # Build Toeplitz covariance matrix
    R = toeplitz(r[:n])
    
    try:
        # Compute log-likelihood
        L = np.linalg.cholesky(R)
        logdet = 2 * np.sum(np.log(np.diag(L)))
        y = np.linalg.solve(L, z)
        quad = np.dot(y, y)
        
        LL = -0.5 * (n * np.log(2 * np.pi) + logdet + quad)
        
        # Innovation variance
        sigmaSq = quad / n
        
    except np.linalg.LinAlgError:
        # Fallback if Cholesky fails
        try:
            logdet = np.linalg.slogdet(R)[1]
            quad = np.dot(z, np.linalg.solve(R, z))
            LL = -0.5 * (n * np.log(2 * np.pi) + logdet + quad)
            sigmaSq = quad / n
        except:
            LL = np.nan
            sigmaSq = np.nan
    
    return {'LL': LL, 'sigmaSq': sigmaSq}





