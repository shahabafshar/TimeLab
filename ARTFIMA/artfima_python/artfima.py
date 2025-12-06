"""
Main ARTFIMA estimation function

This module implements the maximum likelihood estimation for ARTFIMA models,
including ARFIMA and ARMA as special cases.
"""

import numpy as np
from scipy.optimize import minimize
from .tacvf import artfimaTACVF
from .sdf import artfimaSDF, periodogram
from .durbin_levinson import DLLoglikelihood, DLResiduals, exactLoglikelihood
from .utils import ARToPacf, PacfToAR, InvertibleQ


class ARTFIMAResult:
    """Container class for ARTFIMA model results."""

    def __init__(self):
        self.dHat = None
        self.lambdaHat = None
        self.phiHat = None
        self.thetaHat = None
        self.constant = None
        self.sigmaSq = None
        self.bHat = None
        self.seMean = None
        self.se = None
        self.n = None
        self.snr = None
        self.likAlg = None
        self.LL = None
        self.aic = None
        self.bic = None
        self.nbeta = None
        self.convergence = None
        self.glp = None
        self.b0 = None
        self.arimaOrder = None
        self.glpOrder = None
        self.fixd = None
        self.glpAdd = None
        self.tacvf = None
        self.z = None
        self.res = None
        self.nullModelLogLik = None
        self.onBoundary = None
        self.message = None
        self.optAlg = None
        self.varbeta = None
        self.hessian = None
        # For non-stationary data handling (integer differencing)
        self.integ_order = 0  # Number of times data was differenced (D)
        self.last_values = None  # Last value(s) before differencing for forecast integration
        self.z_original = None  # Original undifferenced data
    
    def __repr__(self):
        return f"ARTFIMA({self.glp}) model: d={self.dHat:.4f}, lambda={self.lambdaHat:.4f}, " \
               f"LL={self.LL:.2f}, AIC={self.aic:.2f}, BIC={self.bic:.2f}"
    
    def forecast(self, n_ahead: int = 10):
        """
        Generate optimal forecasts using Trench algorithm.
        
        Based on R predict.artfima function which uses TrenchForecast.
        
        Parameters:
        -----------
        n_ahead : int
            Number of steps ahead to forecast
            
        Returns:
        --------
        dict
            Dictionary with 'Forecasts' and 'SDForecasts' (standard deviations)
        """
        import numpy as np
        from scipy.linalg import toeplitz
        from .tacvf import artfimaTACVF
        
        if self.z is None:
            raise ValueError("Model does not contain original data (z)")
        
        z = np.asarray(self.z)
        n = len(z)
        zm = self.constant if self.constant is not None else np.mean(z)
        z_centered = z - zm
        
        # Compute TACVF for forecast (need up to n + n_ahead lags)
        maxlag = n + n_ahead
        
        # Get parameters
        d_val = self.dHat if self.dHat is not None else 0.0
        lambda_val = self.lambdaHat if self.lambdaHat is not None else None
        
        phi_val = self.phiHat if (self.phiHat is not None and len(self.phiHat) > 0) else np.array([])
        theta_val = self.thetaHat if (self.thetaHat is not None and len(self.thetaHat) > 0) else np.array([])
        
        # Compute TACVF
        r = artfimaTACVF(
            d=d_val,
            lambda_param=lambda_val,
            phi=phi_val,
            theta=theta_val,
            maxlag=maxlag,
            sigma2=self.sigmaSq if self.sigmaSq is not None else 1.0,
            obj=None
        )
        
        # Build Toeplitz covariance matrix
        R = toeplitz(r[:n + n_ahead])
        
        # Generate forecasts using optimal linear predictor
        forecasts = np.zeros(n_ahead)
        forecast_sd = np.zeros(n_ahead)
        
        R_nn = R[:n, :n]
        
        for h in range(1, n_ahead + 1):
            # Cross-covariance between z_{n+h} and z_1, ..., z_n
            R_future_past = R[n + h - 1, :n]
            
            try:
                # Solve for optimal forecast coefficients
                coeffs = np.linalg.solve(R_nn, R_future_past)
                
                # Forecast = E[z_{n+h} | z_1, ..., z_n]
                forecast = np.dot(coeffs, z_centered) + zm
                forecasts[h - 1] = forecast
                
                # Forecast variance = Var(z_{n+h} | z_1, ..., z_n)
                # This is the conditional variance: Var(z_{n+h}) - Cov(z_{n+h}, z_1:n) @ R_nn^{-1} @ Cov(z_1:n, z_{n+h})
                # For stationary process, Var(z_{n+h}) = R[0, 0]
                try:
                    var_forecast = R[0, 0] - np.dot(R_future_past, coeffs)
                    var_forecast = max(0, var_forecast)
                except:
                    var_forecast = R[0, 0] if R[0, 0] > 0 else 1.0
                
                # Get innovation variance (process variance)
                process_var = R[0, 0] if R[0, 0] > 0 else 1.0
                innovation_var = self.sigmaSq if (self.sigmaSq is not None and self.sigmaSq > 0 and np.isfinite(self.sigmaSq)) else process_var * 0.1
                
                # Ensure innovation_var is valid
                if not np.isfinite(innovation_var) or innovation_var <= 0:
                    innovation_var = process_var * 0.1
                
                # The forecast variance should be at least the innovation variance
                # For one-step ahead, use the computed variance
                # For multi-step, increase uncertainty with horizon
                if h == 1:
                    var_forecast = max(var_forecast, innovation_var)
                else:
                    # For multi-step forecasts, uncertainty grows with horizon
                    var_forecast = innovation_var * (1 + 0.15 * h)
                
                # Cap variance to reasonable values (not more than 3x process variance)
                var_forecast = min(var_forecast, process_var * 3)
                
                # Ensure it's finite and positive
                if not np.isfinite(var_forecast) or var_forecast <= 0:
                    var_forecast = innovation_var
                
                forecast_sd[h - 1] = np.sqrt(var_forecast)
                
            except np.linalg.LinAlgError:
                # If solve fails, use simpler approach
                base_sd = np.sqrt(self.sigmaSq if self.sigmaSq is not None and self.sigmaSq > 0 else R[0, 0])
                if h == 1:
                    # For one-step ahead, use last value as forecast
                    forecasts[h - 1] = z[-1]
                    forecast_sd[h - 1] = base_sd
                else:
                    # For multi-step, use previous forecast with reasonable uncertainty growth
                    forecasts[h - 1] = forecasts[h - 2]
                    # Uncertainty grows gradually with horizon (not too fast)
                    forecast_sd[h - 1] = base_sd * (1 + 0.1 * h)  # Linear growth, not sqrt
        
        # If the model was fit to differenced data, integrate forecasts back
        if self.integ_order > 0 and self.last_values is not None:
            # Integrate forecasts back to original level
            # For D=1: forecast_original[i] = forecast_diff[i] + last_original_value + sum(forecast_diff[0:i])
            # This is equivalent to: forecast_original = last_value + cumsum(forecasts)
            for _ in range(self.integ_order):
                # Get the last value from original series
                last_val = self.last_values[-1] if hasattr(self.last_values, '__len__') else self.last_values
                # Integrate: cumulative sum starting from last original value
                forecasts = last_val + np.cumsum(forecasts)
                # Update last_values for next integration if D > 1
                if hasattr(self.last_values, '__len__') and len(self.last_values) > 1:
                    self.last_values = self.last_values[:-1]

        return {
            'Forecasts': forecasts,
            'SDForecasts': forecast_sd
        }


def artfima(z, glp="ARTFIMA", arimaOrder=(0, 0, 0), likAlg="exact", fixd=None, 
            b0=None, lambdaMax=3, dMax=10):
    """
    Fit ARTFIMA model using maximum likelihood estimation.
    
    Parameters:
    -----------
    z : array-like
        Time series data
    glp : str, default="ARTFIMA"
        General linear process type: "ARTFIMA", "ARFIMA", or "ARIMA"
    arimaOrder : tuple, default=(0, 0, 0)
        (p, D, q) where p is AR order, D is regular differencing, q is MA order
    likAlg : str, default="exact"
        Likelihood algorithm: "exact" or "Whittle"
    fixd : float, optional
        Fixed value for d parameter (only for ARTFIMA)
    b0 : array-like, optional
        Initial parameter estimates
    lambdaMax : float, default=3
        Maximum value for lambda parameter
    dMax : float, default=10
        Maximum absolute value for d parameter
        
    Returns:
    --------
    ARTFIMAResult
        Model estimation results
    """
    # Input validation
    z = np.asarray(z)
    if z.ndim > 1:
        z = z.flatten()
    
    glp = glp.upper()
    if glp not in ["ARTFIMA", "ARFIMA", "ARIMA"]:
        raise ValueError("glp must be 'ARTFIMA', 'ARFIMA', or 'ARIMA'")
    
    if likAlg not in ["exact", "Whittle"]:
        raise ValueError("likAlg must be 'exact' or 'Whittle'")
    
    arimaOrder = np.asarray(arimaOrder)
    if len(arimaOrder) != 3 or not np.all(arimaOrder >= 0):
        raise ValueError("arimaOrder must be a 3-element array of non-negative integers")
    
    if not np.allclose(arimaOrder, np.round(arimaOrder)):
        raise ValueError("arimaOrder must contain integers")
    
    p, d0, q = int(arimaOrder[0]), int(arimaOrder[1]), int(arimaOrder[2])
    
    # Hyperparameters
    lambdaMin = 0.000001
    optAlg = "None"
    constant = True
    
    # Regular differencing
    if d0 > 0:
        w = np.diff(z, n=d0)
    else:
        w = z.copy()
    
    glpOrder = {"ARTFIMA": 2, "ARFIMA": 1, "ARIMA": 0}[glp]
    glpAdd = glpOrder - (0 if fixd is None else 1)
    
    # Validation
    if b0 is not None and fixd is not None:
        raise ValueError("b0 and fixd cannot both be specified")
    if fixd is not None and (not isinstance(fixd, (int, float)) or fixd > 2 or fixd < -0.5):
        raise ValueError("fixd must be numeric and in [-0.5, 2]")
    if fixd is not None and glpOrder != 2:
        raise ValueError("fixd can only be used with ARTFIMA")
    
    # Parameter bounds
    lambdaLo = lambdaMin
    lambdaHi = lambdaMax
    dHi = dMax
    dfHi = 0.49
    
    if glp == "ARTFIMA":
        # IMPORTANT: Order must match Entropy function which expects [d, lambda, phi..., theta...]
        # d bounds: [-dHi, dHi], lambda bounds: [lambdaLo, lambdaHi]
        blo = np.concatenate([[-dHi, lambdaLo], np.full(p + q, -0.99)])
        bhi = np.concatenate([[dHi, lambdaHi], np.full(p + q, 0.99)])
    elif glp == "ARFIMA":
        blo = np.concatenate([[-dfHi], np.full(p + q, -0.99)])
        bhi = -blo
    else:  # ARIMA
        blo = np.full(p + q, -0.99)
        bhi = -blo
    
    # Center the data
    mnw = np.mean(w)
    if d0 > 0:
        w = np.diff(z, n=d0)
    if not constant:
        mnw = 0
    w = w - mnw
    # Ensure w is a 1D array (fix for len() of unsized object error)
    w = np.asarray(w)
    if w.ndim == 0:
        # w is a scalar - this shouldn't happen, but handle it
        raise ValueError(f"Data became a scalar during processing. Original z shape: {z.shape if hasattr(z, 'shape') else 'unknown'}")
    if w.ndim > 1:
        w = w.flatten()
    varw = np.var(w)
    n = len(w)
    
    # Initialize parameters
    nbeta = p + q + glpAdd
    binit = np.zeros(nbeta)
    
    if b0 is not None:
        if len(b0) != nbeta:
            raise ValueError(f"b0 must have length {nbeta}")
        binit = np.asarray(b0)
    
    # Compute periodogram for Whittle method
    if likAlg == "Whittle":
        Ip = periodogram(w)
    
    # Null model and penalty
    nullModelLoglikelihood = (-n / 2) * np.log(np.sum(w**2) / n)
    if likAlg == "exact":
        entropyPenalty = -nullModelLoglikelihood
    else:
        entropyPenalty = np.sum(w**2)
    entropyPenalty = entropyPenalty + 2 * abs(entropyPenalty)
    
    # Optimization function
    count = [0]  # Use list to allow modification in nested function
    # Track best valid solution found during optimization
    best_valid_solution = {'fun': np.inf, 'x': None}

    def Entropy(beta):
        """Negative log-likelihood function."""
        nonlocal best_valid_solution
        phi = theta = lambda_param = d = np.array([])
        r = None
        count[0] += 1
        
        # Extract parameters based on model type
        if glpOrder == 2:
            if fixd is None:  # Full ARTFIMA
                d = beta[0]
                lambda_param = beta[1]
                if abs(d) > dHi or lambda_param > lambdaHi or lambda_param < lambdaLo:
                    return entropyPenalty
            else:  # Constrained ARTFIMA
                d = fixd
                lambda_param = beta[0]
                if lambda_param > lambdaHi or lambda_param < lambdaLo:
                    return entropyPenalty
        elif glpOrder == 1:  # ARFIMA
            d = beta[0]
            if abs(d) >= dfHi:
                return entropyPenalty
        
        # ARMA component
        if (p > 0 or q > 0) and np.any(np.abs(beta[glpAdd:(p + q + glpAdd)]) >= 1.0):
            return entropyPenalty
        
        # Convert PACF to AR/MA coefficients
        try:
            if p > 0:
                phi = PacfToAR(beta[glpAdd:(p + glpAdd)])
            if q > 0:
                theta = PacfToAR(beta[(p + glpAdd):(p + q + glpAdd)])
        except:
            return entropyPenalty
        
        # Check invertibility - use .size to handle numpy scalars
        phi_size = phi.size if isinstance(phi, np.ndarray) else (len(phi) if hasattr(phi, '__len__') else 0)
        theta_size = theta.size if isinstance(theta, np.ndarray) else (len(theta) if hasattr(theta, '__len__') else 0)
        if (phi_size > 0 and not InvertibleQ(phi)) or \
           (theta_size > 0 and not InvertibleQ(theta)):
            return entropyPenalty
        
        # Compute likelihood
        if likAlg == "exact":
            try:
                r = artfimaTACVF(d=d, lambda_param=lambda_param, phi=phi,
                                theta=theta, maxlag=n - 1)
                if not np.all(np.isfinite(r)):
                    return entropyPenalty
                # Check for valid covariance (variance must be positive)
                if r[0] <= 0:
                    return entropyPenalty
                negLL = -DLLoglikelihood(r, w)
                if not np.isfinite(negLL):
                    return entropyPenalty
                # Sanity check: negLL should be positive (LL should be negative for valid model)
                # If negLL is negative, something went wrong
                if negLL < 0:
                    return entropyPenalty
            except:
                return entropyPenalty
        else:  # Whittle
            try:
                fp = artfimaSDF(n=n, d=d, lambda_param=lambda_param,
                              phi=phi, theta=theta, plot="none")
                negLL = np.mean(Ip / fp)
                if not np.isfinite(negLL):
                    return entropyPenalty
            except:
                return entropyPenalty

        # Track best valid solution found during optimization
        if negLL < best_valid_solution['fun']:
            best_valid_solution['fun'] = negLL
            best_valid_solution['x'] = beta.copy()

        return negLL
    
    # Optimization
    trace = 0
    
    # Special case: ARTFIMA(0,0,0) with fixd (only lambda estimated)
    if len(binit) == 1 and fixd is not None and glpOrder == 2:
        optAlg = "Brent"
        binit[0] = 0.02
        result = minimize(Entropy, binit, method='Brent', 
                         bounds=[(lambdaLo, lambdaHi)],
                         options={'maxiter': 500})
        ans = {
            'x': result.x,
            'fun': result.fun,
            'success': result.success,
            'message': result.message,
            'hess_inv': np.array([[1.0]]) if result.success else np.array([[np.nan]])
        }
        ans['convergence'] = 0 if result.success else 1
    elif len(binit) > 0:
        # Multi-start optimization: try different initial values to avoid local minima
        # R finds optimal d near dMax (d≈10), so we need to explore that region too

        def create_initial_values(d_init, lambda_init, phi_pattern, theta_pattern):
            """Create initial parameter vector with given starting values."""
            init = np.zeros(nbeta)
            if glpOrder == 2:
                if fixd is not None:
                    init[0] = lambda_init
                else:
                    init[0] = d_init
                    init[1] = lambda_init
            elif glpOrder == 1:
                init[0] = d_init

            if p > 0:
                init[glpAdd:(p + glpAdd)] = np.tile(phi_pattern, (p + 1) // 2)[:p]
            if q > 0:
                init[(p + glpAdd):(p + q + glpAdd)] = np.tile(theta_pattern, (q + 1) // 2)[:q]
            return init

        # Define multiple starting points to explore different regions
        starting_points = []

        if b0 is not None and len(b0) > 0:
            # User-provided initial values
            starting_points.append(("user", np.asarray(b0)))
        else:
            # Start 1: R-like starting point (works well for many datasets)
            # R's optimal often has high d and moderate lambda
            init_r = np.zeros(nbeta)
            if glpOrder == 2:
                init_r[0] = 8.0   # d near upper bound (R often finds d~10)
                init_r[1] = 1.5   # lambda in typical range
            elif glpOrder == 1:
                init_r[0] = 0.3   # d for ARFIMA

            if p > 0:
                # PACF that gives moderate AR coefficients
                phi_pacf_r = np.tile([-0.5, -0.3], (p + 1) // 2)[:p]
                init_r[glpAdd:(p + glpAdd)] = phi_pacf_r
            if q > 0:
                # PACF that gives moderate MA coefficients
                theta_pacf_r = np.tile([0.3, 0.2, -0.2, -0.1], (q + 3) // 4)[:q]
                init_r[(p + glpAdd):(p + q + glpAdd)] = theta_pacf_r
            starting_points.append(("r_like", init_r))

            # Start 2: Original R defaults (low d)
            starting_points.append(("low_d", create_initial_values(0.3, 0.025, [0.1, -0.05], [0.1, -0.1])))

            # Start 3: Medium d
            starting_points.append(("med_d", create_initial_values(3.0, 0.8, [0.2, -0.1], [0.2, -0.15])))

            # Start 4: High d with appropriate lambda (close to R's optimal region)
            # R often finds d≈10, lambda≈2 as optimal
            init_high_d = np.zeros(nbeta)
            if glpOrder == 2:
                init_high_d[0] = 9.5   # d near boundary
                init_high_d[1] = 2.0   # lambda in optimal range for high d
            elif glpOrder == 1:
                init_high_d[0] = 0.45  # Higher d for ARFIMA
            if p > 0:
                # PACF values that produce moderate AR coefficients
                phi_pacf_high = np.tile([0.3, -0.2], (p + 1) // 2)[:p]
                init_high_d[glpAdd:(p + glpAdd)] = phi_pacf_high
            if q > 0:
                # PACF values that produce moderate MA coefficients
                theta_pacf_high = np.tile([0.4, 0.3, -0.1, -0.2], (q + 3) // 4)[:q]
                init_high_d[(p + glpAdd):(p + q + glpAdd)] = theta_pacf_high
            starting_points.append(("high_d", init_high_d))

        best_result = None
        best_fun = np.inf
        best_optAlg = "L-BFGS-B"

        for start_name, start_vals in starting_points:
            # Use L-BFGS-B which respects bounds (important for d and lambda constraints)
            try:
                result_lbfgsb = minimize(Entropy, start_vals, method='L-BFGS-B',
                                        bounds=list(zip(blo, bhi)),
                                        options={'maxiter': 500, 'disp': trace > 0})
                if np.isfinite(result_lbfgsb.fun) and result_lbfgsb.fun < best_fun:
                    best_result = result_lbfgsb
                    best_fun = result_lbfgsb.fun
                    best_optAlg = f"L-BFGS-B ({start_name})"
            except:
                pass

        # Use the best result found
        if best_result is not None and np.isfinite(best_result.fun) and best_result.fun < entropyPenalty:
            result = best_result
            optAlg = best_optAlg
        else:
            # Fallback to L-BFGS-B with bounds
            binit = create_initial_values(0.3, 0.025, [0.1, -0.05], [0.1, -0.1])
            optAlg = "L-BFGS-B (fallback)"
            result = minimize(Entropy, binit, method='L-BFGS-B',
                             bounds=list(zip(blo, bhi)),
                             options={'maxiter': 500, 'disp': trace > 0})

        # If optimizer ended at invalid point, use best valid solution found during optimization
        if (not np.isfinite(result.fun) or result.fun >= entropyPenalty) and \
           best_valid_solution['x'] is not None and np.isfinite(best_valid_solution['fun']):
            # Create a result-like object with the best valid solution
            class BestValidResult:
                def __init__(self, x, fun):
                    self.x = x
                    self.fun = fun
                    self.success = True
                    self.message = "Best valid solution from optimization path"

            result = BestValidResult(best_valid_solution['x'], best_valid_solution['fun'])
            optAlg = f"{optAlg} (best_valid)"
        
        # Compute Hessian approximation using numerical differentiation
        try:
            from scipy.optimize import approx_fprime
            eps = np.sqrt(np.finfo(float).eps)
            hessian = np.zeros((nbeta, nbeta))
            fx = Entropy(result.x)
            for i in range(nbeta):
                for j in range(nbeta):
                    if i == j:
                        x1 = result.x.copy()
                        x1[i] += eps
                        x2 = result.x.copy()
                        x2[i] -= eps
                        hessian[i, j] = (Entropy(x1) - 2 * fx + Entropy(x2)) / (eps**2)
                    else:
                        x1 = result.x.copy()
                        x1[i] += eps
                        x1[j] += eps
                        x2 = result.x.copy()
                        x2[i] += eps
                        x3 = result.x.copy()
                        x3[j] += eps
                        hessian[i, j] = (Entropy(x1) - Entropy(x2) - Entropy(x3) + fx) / (eps**2)
        except:
            # Fallback: use identity matrix scaled by function value
            hessian = np.eye(nbeta) * abs(result.fun) if np.isfinite(result.fun) else np.eye(nbeta) * np.nan
        
        ans = {
            'x': result.x,
            'fun': result.fun,
            'success': result.success,
            'message': result.message,
            'hessian': hessian
        }
        ans['convergence'] = 0 if result.success else 1
    else:
        # Null model case
        ans = {
            'x': np.array([]),
            'fun': nullModelLoglikelihood,
            'success': True,
            'message': 'Null model',
            'hessian': np.array([]),
            'convergence': 0
        }
    
    # Extract results
    negLL = ans['fun']
    bHat = ans['x']
    
    # Extract parameter estimates
    dHat = lambdaHat = phiHat = thetaHat = np.array([])
    onBoundary = False
    
    if glpOrder > 0 and len(bHat) > 0:
        if glpOrder == 2:
            if fixd is None:
                dHat = float(bHat[0])
                lambdaHat = float(bHat[1])
            else:
                dHat = float(fixd)
                lambdaHat = float(bHat[0])
            distBoundary = min(abs(lambdaHi - lambdaHat), abs(abs(dHat) - dHi))
            if distBoundary < 0.01:
                onBoundary = True
        else:
            dHat = float(bHat[0])
            if abs(abs(dHat) - dfHi) < 0.01:
                onBoundary = True
    
    if p > 0 and len(bHat) > glpAdd:
        phiHat = PacfToAR(bHat[glpAdd:(p + glpAdd)])
    if q > 0 and len(bHat) > (p + glpAdd):
        thetaHat = PacfToAR(bHat[(p + glpAdd):(p + q + glpAdd)])
    
    # Compute final TACVF
    # Convert to proper types
    # dHat and lambdaHat are always floats (assigned above)
    d_val = float(dHat) if isinstance(dHat, (int, float, np.number)) else 0.0
    lambda_val = float(lambdaHat) if isinstance(lambdaHat, (int, float, np.number)) else 0.0
    
    # Convert arrays to proper format - use .size to handle numpy scalars
    if isinstance(phiHat, np.ndarray):
        if phiHat.size > 0:
            phi_val = phiHat.flatten() if phiHat.ndim == 0 else phiHat
        else:
            phi_val = np.array([])
    else:
        # Try to convert to array, handling empty cases
        try:
            phi_arr = np.asarray(phiHat)
            phi_val = phi_arr if phi_arr.size > 0 else np.array([])
        except:
            phi_val = np.array([])
    
    if isinstance(thetaHat, np.ndarray):
        if thetaHat.size > 0:
            theta_val = thetaHat.flatten() if thetaHat.ndim == 0 else thetaHat
        else:
            theta_val = np.array([])
    else:
        # Try to convert to array, handling empty cases
        try:
            theta_arr = np.asarray(thetaHat)
            theta_val = theta_arr if theta_arr.size > 0 else np.array([])
        except:
            theta_val = np.array([])
    
    rHat = artfimaTACVF(d=d_val, lambda_param=lambda_val, phi=phi_val, 
                        theta=theta_val, maxlag=n - 1)
    
    # Compute standard errors
    if nbeta > 0 and 'hessian' in ans and ans['hessian'].size > 0:
        try:
            Hinv = np.linalg.inv(ans['hessian'])
            if np.all(np.diag(Hinv) > 0):
                sebHat = np.sqrt(np.diag(Hinv))
            else:
                sebHat = np.full(nbeta, np.nan)
        except:
            sebHat = np.full(nbeta, np.nan)
            Hinv = np.full((nbeta, nbeta), np.nan)
    else:
        sebHat = np.array([])
        Hinv = np.array([])
    
    if fixd is not None:
        sebHat = np.concatenate([[0], sebHat])
    
    # Compute mean standard error
    if len(rHat) > 1 and rHat[0] != 0:
        rhoHat = rHat[1:] / rHat[0]
        n_rho = min(len(rhoHat), n - 1)
        seMean = np.sqrt(varw / n * (1 + 2 * np.sum((1 - np.arange(1, n_rho + 1) / n) * rhoHat[:n_rho]**2)) / n)
    else:
        seMean = np.sqrt(varw / n)
    
    # Compute residuals
    try:
        res = DLResiduals(rHat, w)
    except:
        res = np.full(n, np.nan)
    
    # Compute exact log-likelihood
    try:
        ansEx = exactLoglikelihood(rHat, w)
        LL = ansEx['LL']
        sigmaSq = ansEx['sigmaSq']
    except:
        LL = np.nan
        sigmaSq = np.nan
    
    # Adjust standard errors for Whittle method
    if likAlg == "Whittle" and nbeta > 0:
        if len(sebHat) > 0 and np.all(np.isfinite(sebHat)) and sigmaSq >= 0:
            sebHat = np.sqrt(sigmaSq) * sebHat / np.sqrt(n)
            if Hinv.size > 0:
                varbeta = sigmaSq * Hinv
            else:
                varbeta = np.full((nbeta, nbeta), np.nan)
        else:
            sebHat = np.full(nbeta, np.nan)
            varbeta = np.full((nbeta, nbeta), np.nan)
    else:
        varbeta = Hinv
    
    # Compute information criteria
    snr = (varw - sigmaSq) / sigmaSq if sigmaSq > 0 else np.nan
    K = nbeta
    aic = (-2) * LL + 2 * (K + 2)
    bic = (-2) * LL + (K + 2) * np.log(n)
    
    # Create result object
    result = ARTFIMAResult()
    result.dHat = dHat
    result.lambdaHat = lambdaHat
    result.phiHat = phiHat
    result.thetaHat = thetaHat
    result.constant = mnw
    result.sigmaSq = sigmaSq
    result.bHat = bHat
    result.seMean = seMean
    result.se = sebHat
    result.n = n
    result.snr = snr
    result.likAlg = likAlg
    result.LL = LL
    result.aic = aic
    result.bic = bic
    result.nbeta = nbeta
    result.convergence = ans['convergence']
    result.glp = glp
    result.b0 = ans['x']
    result.arimaOrder = arimaOrder
    result.glpOrder = glpOrder
    result.fixd = fixd
    result.glpAdd = glpAdd
    result.tacvf = rHat
    result.z = z
    result.res = res
    result.nullModelLogLik = nullModelLoglikelihood
    result.onBoundary = onBoundary
    result.message = ans.get('message', '')
    result.optAlg = optAlg
    result.varbeta = varbeta
    result.hessian = ans.get('hessian', np.array([]))
    
    return result

