"""
ACF/PACF analysis service - adapted from arauto/lib/find_acf_pacf.py
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from typing import Dict, Any


class ACFPACFService:
    """Service for ACF/PACF analysis and parameter estimation"""
    
    @staticmethod
    def find_acf_pacf(timeseries: pd.Series, seasonality: int) -> Dict[str, Any]:
        """
        Calculate ACF/PACF and estimate model parameters
        
        Adapted from arauto/lib/find_acf_pacf.py
        
        Args:
            timeseries: Time series to analyze
            seasonality: Seasonal frequency
            
        Returns:
            Dict with ACF/PACF values and suggested parameters
        """
        # Clean data
        ts_clean = timeseries.dropna()
        
        # Calculate confidence intervals
        n = len(ts_clean)
        lower_conf_int = -1.96 / np.sqrt(n)
        upper_conf_int = 1.96 / np.sqrt(n)
        
        # Calculate lags (seasonality * 2)
        max_lags = seasonality * 2
        
        # Calculate PACF
        # Using 'yw' (Yule-Walker) method - valid methods: 'ols', 'yw', 'ywadjusted', 'ywmle', 'ld', 'burg'
        pacf_values = sm.tsa.stattools.pacf(
            ts_clean,
            nlags=max_lags,
            method='yw'  # Changed from 'ywunbiased' to 'yw' (Yule-Walker)
        )
        
        # Calculate ACF
        # Note: 'unbiased' parameter was removed in newer statsmodels versions
        # Use 'adjusted' instead if needed, or omit for default behavior
        acf_values = sm.tsa.stattools.acf(
            ts_clean,
            nlags=max_lags,
            fft=False
        )
        
        # Estimate p terms (AR) from PACF
        p_terms = 0
        for value in pacf_values[1:]:
            if value >= upper_conf_int or value <= lower_conf_int:
                p_terms += 1
            else:
                break
        
        # Estimate q terms (MA) from ACF
        # Cap q to avoid conflicts with seasonal component (q should be < seasonality)
        q_terms = 0
        max_q = min(seasonality - 1, len(acf_values) - 1)  # Cap q to avoid seasonal overlap
        for i, value in enumerate(acf_values[1:max_q + 1], start=1):
            if value >= upper_conf_int or value <= lower_conf_int:
                q_terms += 1
            else:
                break
        
        # Estimate P terms (Seasonal AR) from PACF
        P_terms = 0
        if seasonality <= len(pacf_values) - 1:
            if (pacf_values[seasonality] >= upper_conf_int or
                pacf_values[seasonality] <= lower_conf_int):
                P_terms += 1
                if (seasonality * 2 <= len(pacf_values) - 1 and
                    (pacf_values[seasonality * 2] >= upper_conf_int or
                     pacf_values[seasonality * 2] <= lower_conf_int)):
                    P_terms += 1
        
        # Estimate Q terms (Seasonal MA) from ACF
        Q_terms = 0
        if seasonality <= len(acf_values) - 1:
            if (acf_values[seasonality] >= upper_conf_int or
                acf_values[seasonality] <= lower_conf_int):
                Q_terms += 1
                if (seasonality * 2 <= len(acf_values) - 1 and
                    (acf_values[seasonality * 2] >= upper_conf_int or
                     acf_values[seasonality * 2] <= lower_conf_int)):
                    Q_terms += 1
        
        # Prepare result
        lags = list(range(max_lags + 1))
        
        return {
            "acf": acf_values.tolist(),
            "pacf": pacf_values.tolist(),
            "lags": lags,
            "confidence_interval": {
                "lower": float(lower_conf_int),
                "upper": float(upper_conf_int)
            },
            "suggested_parameters": {
                "p": int(p_terms),
                "q": int(q_terms),
                "P": int(P_terms),
                "Q": int(Q_terms)
            }
        }

