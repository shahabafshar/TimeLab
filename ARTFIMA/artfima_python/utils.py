"""
Utility functions for ARTFIMA models

Includes functions for converting between AR coefficients and partial
autocorrelation function (PACF) coefficients.
"""

import numpy as np


def ARToPacf(phi):
    """
    Convert AR coefficients to partial autocorrelation function (PACF).
    
    Parameters:
    -----------
    phi : array-like
        AR coefficients
        
    Returns:
    --------
    numpy.ndarray
        PACF coefficients
    """
    phi = np.asarray(phi)
    L = len(phi)
    if L == 0:
        return np.array([])
    
    phik = phi.copy()
    pi = np.zeros(L)
    
    for k in range(1, L + 1):
        LL = L + 1 - k
        a = phik[LL - 1]
        pi[L - k] = a
        
        if abs(a) == 1:
            break
        
        phikp1 = np.delete(phik, LL - 1)
        phik = (phikp1 + a * phikp1[::-1]) / (1 - a**2)
    
    return pi


def PacfToAR(pi):
    """
    Convert partial autocorrelation function (PACF) to AR coefficients.
    
    Parameters:
    -----------
    pi : array-like
        PACF coefficients
        
    Returns:
    --------
    numpy.ndarray
        AR coefficients
    """
    pi = np.asarray(pi)
    L = len(pi)
    if L == 0:
        return np.array([])
    if L == 1:
        return pi
    
    phik = np.array([pi[0]])
    for k in range(2, L + 1):
        phikm1 = phik.copy()
        phik = np.concatenate([phikm1 - pi[k-1] * phikm1[::-1], [pi[k-1]]])
    
    return phik


def InvertibleQ(phi):
    """
    Check if AR coefficients represent an invertible process.
    
    Parameters:
    -----------
    phi : array-like
        AR coefficients
        
    Returns:
    --------
    bool
        True if invertible, False otherwise
    """
    if len(phi) == 0:
        return True
    try:
        pacf = ARToPacf(phi)
        return np.all(np.abs(pacf) < 1)
    except:
        return False





