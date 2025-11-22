"""
ARTFIMA model training service
"""
import sys
import os
import numpy as np
import pandas as pd
import pickle
import base64
from typing import Optional, Dict, Any
from pathlib import Path

# Add ARTFIMA package to path
# Try multiple possible paths - add parent directory so we can import artfima_python as a package
possible_paths = [
    Path(__file__).parent.parent.parent.parent.parent / "ARTFIMA",  # From project root
    Path(__file__).parent.parent.parent.parent / "ARTFIMA",  # Alternative
    Path.cwd() / "ARTFIMA",  # Current working directory
]

artfima_path = None
for path in possible_paths:
    artfima_python_path = path / "artfima_python"
    if artfima_python_path.exists() and (artfima_python_path / "__init__.py").exists():
        artfima_path = path
        break

if artfima_path and str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

try:
    from artfima_python import artfima as artfima_fit
except ImportError as e:
    raise ImportError(
        f"Failed to import ARTFIMA package. Tried paths: {[str(p) for p in possible_paths]}. "
        f"Original error: {str(e)}"
    )


class ARTFIMATrainingService:
    """Service for training ARTFIMA models"""
    
    @staticmethod
    def train_artfima(
        Y: pd.Series,
        p: int = 0,
        d: float = 0.0,
        q: int = 0,
        glp: str = "ARTFIMA",
        lambda_param: Optional[float] = None,
        fixd: Optional[float] = None,
        likAlg: str = "exact",
        quiet: bool = True
    ) -> Dict[str, Any]:
        """
        Train an ARTFIMA model
        
        Args:
            Y: Time series data
            p: AR order
            d: Fractional differencing parameter (can be fractional)
            q: MA order
            glp: General linear process type ("ARTFIMA", "ARFIMA", or "ARIMA")
            lambda_param: Tempering parameter (only for ARTFIMA)
            fixd: Fixed d parameter (optional, only for ARTFIMA)
            likAlg: Likelihood algorithm ("exact" or "Whittle")
            quiet: Suppress output
            
        Returns:
            Dict with model results and metadata
        """
        # Validate parameters
        if p < 0 or q < 0:
            raise ValueError("AR/MA parameters must be non-negative")
        if glp not in ["ARTFIMA", "ARFIMA", "ARIMA"]:
            raise ValueError("glp must be 'ARTFIMA', 'ARFIMA', or 'ARIMA'")
        
        # Validate time series data
        if Y is None:
            raise ValueError("Time series data is None")
        
        # Convert pandas Series to numpy array for ARTFIMA
        # CRITICAL: Must ensure it's a proper 1D numpy array, not a scalar
        if isinstance(Y, pd.Series):
            # Get values and ensure it's a proper array
            z_raw = Y.values
        else:
            z_raw = Y
        
        # Convert to list first, then to numpy array - this ensures proper 1D shape
        # This is the most reliable way to ensure we get a 1D array
        if isinstance(z_raw, np.ndarray):
            if z_raw.ndim == 0:
                raise ValueError("Time series data is a scalar, not an array")
            z_list = z_raw.flatten().tolist()
        elif isinstance(z_raw, (list, tuple)):
            z_list = list(z_raw)
        else:
            # Try to convert to list
            try:
                z_list = [float(x) for x in z_raw]
            except (TypeError, ValueError):
                raise ValueError(f"Cannot convert time series data to list. Type: {type(z_raw)}")
        
        if len(z_list) == 0:
            raise ValueError("Time series data is empty")
        
        # Create numpy array from list - this guarantees 1D shape
        z = np.array(z_list, dtype=np.float64)
        
        # Verify it's 1D
        if z.ndim != 1:
            raise ValueError(f"Time series data has wrong dimensions: {z.ndim}, expected 1")
        if len(z) == 0:
            raise ValueError("Time series data is empty after conversion")
        
        # Remove any NaN or Inf values BEFORE length validation
        # This is important because cleaning can reduce the length
        z_original_length = len(z)
        finite_mask = np.isfinite(z)
        z = z[finite_mask]
        
        if len(z) == 0:
            raise ValueError(
                f"Time series data contains no finite values "
                f"(original length: {z_original_length})"
            )
        
        # Now validate length AFTER cleaning (this is the actual usable data)
        min_required_length = max(p, q, 1) + 20  # Extra buffer for differencing and estimation
        if len(z) < min_required_length:
            raise ValueError(
                f"Time series is too short after cleaning ({len(z)} observations, "
                f"original: {z_original_length}). "
                f"Need at least {min_required_length} finite observations for p={p}, q={q}. "
                f"Consider reducing p or q, or using a longer time series."
            )
        
        # Final check: ensure z is a proper 1D array that will work with ARTFIMA
        # Make sure it's contiguous and has the right shape
        z = np.ascontiguousarray(z, dtype=np.float64)
        if z.ndim != 1:
            raise ValueError(f"Final array has wrong dimensions: {z.ndim}, shape: {z.shape}")
        
        # Determine arimaOrder (regular differencing)
        # ARTFIMA handles fractional d internally, so we use d0=0 for regular differencing
        # and let ARTFIMA handle the fractional part
        d0 = 0  # Regular differencing (ARTFIMA uses fractional d internally)
        arimaOrder = (int(p), int(d0), int(q))  # Ensure integers
        
        # Call ARTFIMA fitting function
        try:
            # z is already validated and cleaned above
            # Just ensure it's in the exact format ARTFIMA expects
            # ARTFIMA expects a 1D numpy array that supports .copy()
            z_clean = np.asarray(z, dtype=np.float64)
            
            # Force reshape to 1D if needed (shouldn't be needed, but be safe)
            if z_clean.ndim == 0:
                raise ValueError("Time series data is a scalar - this should not happen")
            z_clean = z_clean.reshape(-1)  # Force to 1D
            
            # Verify it's actually 1D
            if z_clean.ndim != 1:
                raise ValueError(f"Time series data has wrong dimensions: {z_clean.ndim}, shape: {z_clean.shape}")
            
            # Test that .copy() works and produces a proper array
            z_test = z_clean.copy()
            if z_test.ndim != 1 or len(z_test) != len(z_clean):
                raise ValueError("Time series array copy failed validation")
            
            # Ensure arimaOrder is a proper tuple
            arimaOrder_clean = (int(p), int(d0), int(q))
            
            # Final validation before calling ARTFIMA
            if len(z_clean) == 0:
                raise ValueError("Time series data is empty")
            if any(x < 0 for x in arimaOrder_clean):
                raise ValueError(f"arimaOrder values must be non-negative, got {arimaOrder_clean}")
            
            result = artfima_fit(
                z=z_clean,
                glp=glp,
                arimaOrder=arimaOrder_clean,
                likAlg=likAlg,
                fixd=fixd,
                b0=None,
                lambdaMax=3,
                dMax=10
            )
        except ValueError as e:
            # Re-raise ValueError with more context
            raise ValueError(f"ARTFIMA model fitting failed: {str(e)}")
        except Exception as e:
            # Provide more detailed error information
            error_msg = str(e)
            if "len()" in error_msg or "unsized" in error_msg:
                raise ValueError(
                    f"ARTFIMA model fitting failed: Data shape issue. "
                    f"Time series length: {len(z)}, p={p}, q={q}. "
                    f"Original error: {error_msg}"
                )
            raise ValueError(f"ARTFIMA model fitting failed: {error_msg}")
        
        # Serialize model result
        model_data = ARTFIMATrainingService._serialize_model(result)
        
        # Create summary text
        d_val = result.dHat
        if isinstance(d_val, (list, np.ndarray)) and len(d_val) > 0:
            d_val = float(d_val[0])
        elif not isinstance(d_val, (int, float, np.number)):
            d_val = 0.0
        
        lambda_val = result.lambdaHat
        if isinstance(lambda_val, (list, np.ndarray)) and len(lambda_val) > 0:
            lambda_val = float(lambda_val[0])
        elif lambda_val is None or (isinstance(lambda_val, (list, np.ndarray)) and len(lambda_val) == 0):
            lambda_val = None
        
        summary_lines = [
            f"ARTFIMA Model Summary",
            f"Model Type: {result.glp}",
            f"Parameters: p={p}, d={d_val:.6f}, q={q}",
        ]
        if lambda_val is not None:
            summary_lines.append(f"Lambda: {lambda_val:.6f}")
        # Format values properly (can't use conditional in format specifier)
        ll_str = f"{result.LL:.4f}" if result.LL is not None else "N/A"
        aic_str = f"{result.aic:.4f}" if result.aic is not None else "N/A"
        bic_str = f"{result.bic:.4f}" if result.bic is not None else "N/A"
        
        summary_lines.extend([
            f"Log-likelihood: {ll_str}",
            f"AIC: {aic_str}",
            f"BIC: {bic_str}",
            f"Convergence: {result.convergence}",
        ])
        summary = "\n".join(summary_lines)
        
        # Extract metrics
        metrics = {
            "aic": float(result.aic) if result.aic is not None and np.isfinite(result.aic) else None,
            "bic": float(result.bic) if result.bic is not None and np.isfinite(result.bic) else None,
            "hqic": None,  # ARTFIMA doesn't provide HQIC
            "ll": float(result.LL) if result.LL is not None and np.isfinite(result.LL) else None,
        }
        
        # Prepare parameters dict
        d_val = result.dHat
        if isinstance(d_val, (list, np.ndarray)) and len(d_val) > 0:
            d_val = float(d_val[0])
        elif not isinstance(d_val, (int, float, np.number)):
            d_val = 0.0
        
        lambda_val = result.lambdaHat
        if isinstance(lambda_val, (list, np.ndarray)) and len(lambda_val) > 0:
            lambda_val = float(lambda_val[0])
        elif lambda_val is None or (isinstance(lambda_val, (list, np.ndarray)) and len(lambda_val) == 0):
            lambda_val = None
        
        params_dict = {
            "p": p,
            "d": float(d_val),
            "q": q,
            "glp": glp,
        }
        if lambda_val is not None:
            params_dict["lambda"] = float(lambda_val)
        
        return {
            "model_data": model_data,
            "summary": summary,
            "metrics": metrics,
            "parameters": params_dict,
            "artfima_result": result,  # Store full result for forecast generation
        }
    
    @staticmethod
    def _serialize_model(model) -> str:
        """Serialize ARTFIMA model result to base64 string"""
        pickled = pickle.dumps(model)
        return base64.b64encode(pickled).decode('utf-8')
    
    @staticmethod
    def deserialize_model(model_data: str):
        """Deserialize ARTFIMA model from base64 string"""
        pickled = base64.b64decode(model_data.encode('utf-8'))
        return pickle.loads(pickled)

