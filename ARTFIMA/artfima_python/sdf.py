"""
Spectral Density Function (SDF) for ARTFIMA models
"""

import numpy as np


def sdfarfima(n, d=0, phi=None, theta=None):
    """
    Spectral density function for ARFIMA model.
    
    Parameters:
    -----------
    n : int
        Sample size
    d : float, default=0
        Fractional differencing parameter
    phi : array-like, optional
        AR coefficients
    theta : array-like, optional
        MA coefficients
        
    Returns:
    --------
    numpy.ndarray
        Spectral density at Fourier frequencies
    """
    if phi is None:
        phi = np.array([])
    else:
        phi = np.asarray(phi)
    if theta is None:
        theta = np.array([])
    else:
        theta = np.asarray(theta)
    
    lams = 2 * np.pi * np.arange(1/n, 0.5 + 1/n, 1/n)
    nf = len(lams)
    
    # MA part (numerator)
    if len(theta) > 0:
        a = np.outer(lams, np.arange(1, len(theta) + 1))
        C = np.column_stack([np.ones(nf), np.cos(a)]) @ np.concatenate([[1], -theta])
        S = np.sin(a) @ theta
    else:
        C = np.ones(nf)
        S = np.zeros(nf)
    
    num = C**2 + S**2
    
    # AR part (denominator)
    if len(phi) > 0:
        a = np.outer(lams, np.arange(1, len(phi) + 1))
        C = np.column_stack([np.ones(nf), np.cos(a)]) @ np.concatenate([[1], -phi])
        S = np.sin(a) @ phi
    else:
        C = np.ones(nf)
        S = np.zeros(nf)
    
    den = C**2 + S**2
    s1 = num / den
    
    # Fractional part
    if d == 0:
        s2 = np.ones(nf)
    else:
        s2 = (2 * np.sin(lams / 2)) ** (-2 * d)
    
    return s1 * s2


def sdffi(n, d, lambda_param):
    """
    Spectral density function for tempered fractional integration.
    
    Parameters:
    -----------
    n : int
        Sample size
    d : float
        Fractional differencing parameter
    lambda_param : float
        Tempering parameter
        
    Returns:
    --------
    numpy.ndarray
        Spectral density at Fourier frequencies
    """
    w = 2 * np.pi * np.arange(1/n, 0.5 + 1/n, 1/n)
    return (1 + np.exp(-2 * lambda_param) - (2 * np.cos(w)) / np.exp(lambda_param)) ** (-d)


def artfimaSDF(n=100, d=0, lambda_param=0, phi=None, theta=None, obj=None, plot="none"):
    """
    Spectral density function for ARTFIMA model.
    
    Parameters:
    -----------
    n : int, default=100
        Sample size
    d : float, default=0
        Fractional differencing parameter
    lambda_param : float, default=0
        Tempering parameter
    phi : array-like, optional
        AR coefficients
    theta : array-like, optional
        MA coefficients
    obj : object, optional
        ARTFIMA model object
    plot : str, default="none"
        Plot option ("none", "log", "loglog")
        
    Returns:
    --------
    numpy.ndarray
        Spectral density at Fourier frequencies
    """
    if obj is not None:
        if hasattr(obj, 'dHat'):
            d = obj.dHat
            lambda_param = obj.lambdaHat
            phi = obj.phiHat
            theta = obj.thetaHat
    
    if phi is None:
        phi = np.array([])
    else:
        phi = np.asarray(phi)
    if theta is None:
        theta = np.array([])
    else:
        theta = np.asarray(theta)
    
    lams = 2 * np.pi * np.arange(1/n, 0.5 + 1/n, 1/n)
    
    if lambda_param == 0 or (isinstance(lambda_param, (int, float)) and lambda_param == 0):
        s = sdfarfima(n, d=d, phi=phi, theta=theta)
        if plot != "none":
            import matplotlib.pyplot as plt
            if plot == "log":
                plt.plot(lams, np.log(s))
                plt.xlabel("frequency")
                plt.ylabel("log sdf")
            else:
                plt.plot(np.log(lams), np.log(s))
                plt.xlabel("log frequency")
                plt.ylabel("log sdf")
            plt.show()
        return s
    
    nf = len(lams)
    
    # MA part (numerator)
    if len(theta) > 0:
        a = np.outer(lams, np.arange(1, len(theta) + 1))
        C = np.column_stack([np.ones(nf), np.cos(a)]) @ np.concatenate([[1], -theta])
        S = np.sin(a) @ theta
    else:
        C = np.ones(nf)
        S = np.zeros(nf)
    
    num = C**2 + S**2
    
    # AR part (denominator)
    if len(phi) > 0:
        a = np.outer(lams, np.arange(1, len(phi) + 1))
        C = np.column_stack([np.ones(nf), np.cos(a)]) @ np.concatenate([[1], -phi])
        S = np.sin(a) @ phi
    else:
        C = np.ones(nf)
        S = np.zeros(nf)
    
    den = C**2 + S**2
    s1 = num / den
    
    # Tempered fractional part
    s2 = (1 + np.exp(-2 * lambda_param) - (2 * np.cos(lams)) / np.exp(lambda_param)) ** (-d)
    s = s1 * s2
    
    if plot != "none":
        import matplotlib.pyplot as plt
        if plot == "log":
            plt.plot(lams, np.log(s))
            plt.xlabel("frequency")
            plt.ylabel("log sdf")
        else:
            plt.plot(np.log(lams), np.log(s))
            plt.xlabel("log frequency")
            plt.ylabel("log sdf")
        plt.show()
    
    return s


def periodogram(z):
    """
    Compute periodogram of time series.
    
    This matches the R spec.pgram function with fast=FALSE, detrend=FALSE, 
    plot=FALSE, taper=0, log="no", type="h".
    
    Parameters:
    -----------
    z : array-like
        Time series data
        
    Returns:
    --------
    numpy.ndarray
        Periodogram values at Fourier frequencies (positive frequencies only)
    """
    z = np.asarray(z)
    n = len(z)
    z_centered = z - np.mean(z)
    
    # Compute FFT
    fft_vals = np.fft.fft(z_centered, n=n)
    
    # Periodogram at positive frequencies only (1/n to 1/2)
    # R's spec.pgram returns spec at frequencies 1/n, 2/n, ..., floor((n-1)/2)/n
    n_freqs = (n - 1) // 2
    freqs_idx = np.arange(1, n_freqs + 1)
    spec = np.abs(fft_vals[freqs_idx]) ** 2 / n
    
    return spec

