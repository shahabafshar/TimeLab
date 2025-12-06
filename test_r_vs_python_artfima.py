"""
Test script to compare R and Python ARTFIMA implementations
Uses the same parameters from the UI:
- p = 3, q = 11
- glp = "ARTFIMA"
- Data: CO2 levels (differenced once for stationarity)
"""
import sys
import os
import numpy as np
import pandas as pd
from pathlib import Path
import subprocess
import tempfile
import json

# Add ARTFIMA package to path
artfima_path = Path(__file__).parent / "ARTFIMA"
if str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

from artfima_python import artfima as artfima_fit

def load_co2_data():
    """Load CO2 sample data"""
    data_path = Path(__file__).parent / "backend" / "data" / "samples" / "co2_levels.csv"
    if not data_path.exists():
        # Try alternative paths
        alt_paths = [
            Path(__file__).parent / "backend" / "app" / "data" / "samples" / "co2_levels.csv",
            Path(__file__).parent / "samples" / "co2_levels.csv",
        ]
        for alt_path in alt_paths:
            if alt_path.exists():
                data_path = alt_path
                break

    df = pd.read_csv(data_path)
    print(f"Loaded CO2 data: {len(df)} observations")
    print(f"Date range: {df['date'].iloc[0]} to {df['date'].iloc[-1]}")
    print(f"CO2 range: {df['co2'].min():.2f} to {df['co2'].max():.2f}")
    return df['co2'].values

def run_python_artfima(z, p=3, q=11, glp="ARTFIMA"):
    """Run Python ARTFIMA implementation"""
    print("\n" + "="*60)
    print("PYTHON ARTFIMA IMPLEMENTATION")
    print("="*60)

    # Apply differencing (as done in the service)
    z_diff = np.diff(z)
    print(f"Original data length: {len(z)}")
    print(f"Differenced data length: {len(z_diff)}")
    print(f"Last value before diff: {z[-1]:.4f}")

    # Fit ARTFIMA
    result = artfima_fit(
        z=z_diff,
        glp=glp,
        arimaOrder=(p, 0, q),
        likAlg="exact",
        fixd=None,
        b0=None,
        lambdaMax=3,
        dMax=10
    )

    # Get sigma2/snr value (Python uses snr)
    sigma2 = getattr(result, 'snr', 1.0)

    print(f"\nEstimated Parameters:")
    print(f"  d (fractional diff): {result.dHat:.6f}")
    print(f"  lambda (tempering):  {result.lambdaHat:.6f}")
    print(f"  snr (signal/noise):  {sigma2:.6f}")
    print(f"\nAR coefficients (phi): {result.phiHat}")
    print(f"MA coefficients (theta): {result.thetaHat}")
    print(f"\nModel Fit:")
    print(f"  Log-likelihood: {result.LL:.4f}")
    print(f"  AIC: {result.aic:.4f}")
    print(f"  BIC: {result.bic:.4f}")
    print(f"  Convergence: {result.convergence}")

    # Store for forecast integration - use original (undifferenced) data's last value
    result.integ_order = 1
    result.last_values = np.array([z[-1]])  # z is original data before differencing

    # Generate forecast
    n_ahead = 12
    forecast_result = result.forecast(n_ahead=n_ahead)
    forecasts = forecast_result['Forecasts']
    forecast_sd = forecast_result['SDForecasts']

    print(f"\nForecasts (next {n_ahead} periods) - after integration:")
    for i, (fc, sd) in enumerate(zip(forecasts, forecast_sd)):
        ci_lower = fc - 1.96 * sd
        ci_upper = fc + 1.96 * sd
        print(f"  Period {i+1}: {fc:.2f} [{ci_lower:.2f}, {ci_upper:.2f}]")

    return {
        'd': result.dHat,
        'lambda': result.lambdaHat,
        'sigma2': sigma2,
        'phi': result.phiHat.tolist() if hasattr(result.phiHat, 'tolist') else result.phiHat,
        'theta': result.thetaHat.tolist() if hasattr(result.thetaHat, 'tolist') else result.thetaHat,
        'LL': result.LL,
        'aic': result.aic,
        'bic': result.bic,
        'forecasts': forecasts.tolist(),
        'forecast_sd': forecast_sd.tolist()
    }

def create_r_script(data_file, p=3, q=11, glp="ARTFIMA"):
    """Create R script for ARTFIMA comparison using local artfima source"""
    # Path to local artfima R source files
    artfima_r_path = str(Path(__file__).parent / "ARTFIMA" / "artfima" / "R").replace('\\', '/')

    r_script = f'''
# R ARTFIMA comparison script using LOCAL artfima source
# Load required packages
library(gsl)   # For hypergeometric function hyperg_2F1
library(ltsa)  # For TrenchForecast

# Source all required R files from local artfima package
artfima_path <- "{artfima_r_path}"
r_files <- c(
    "artfimaTACVF.R",
    "ifisher.R",
    "InvertibleQ.R",
    "Periodogram.R",
    "tseg.R",
    "artfimaSDF.R",
    "artfima.R",
    "predict.artfima.R",
    "print.artfima.R",
    "plot.artfima.R"
)
for(f in r_files) {{
    source(file.path(artfima_path, f))
}}

# Load data
data <- read.csv("{data_file}")
z <- data$co2

cat("\\n", paste(rep("=", 60), collapse=""), "\\n")
cat("R ARTFIMA IMPLEMENTATION\\n")
cat(paste(rep("=", 60), collapse=""), "\\n")

cat("Original data length:", length(z), "\\n")
cat("CO2 range:", min(z), "to", max(z), "\\n")

# Apply differencing (same as Python)
z_diff <- diff(z)
cat("Differenced data length:", length(z_diff), "\\n")
cat("Last value before diff:", z[length(z)], "\\n")

# Fit ARTFIMA model
result <- artfima(z_diff, glp="{glp}", arimaOrder=c({p}, 0, {q}))

cat("\\nEstimated Parameters:\\n")
cat("  d (fractional diff):", result$dHat, "\\n")
cat("  lambda (tempering): ", result$lambdaHat, "\\n")
cat("  sigma2 (variance):  ", result$sigma2Hat, "\\n")

cat("\\nAR coefficients (phi):", result$phiHat, "\\n")
cat("MA coefficients (theta):", result$thetaHat, "\\n")

cat("\\nModel Fit:\\n")
cat("  Log-likelihood:", result$LL, "\\n")
cat("  AIC:", result$aic, "\\n")
cat("  BIC:", result$bic, "\\n")
cat("  Convergence:", result$convergence, "\\n")

# Generate forecast
n_ahead <- 12
fc <- predict(result, n.ahead=n_ahead)

# Integrate forecasts (add back last value + cumsum)
last_val <- z[length(z)]
forecasts <- last_val + cumsum(fc$Forecasts)

cat("\\nForecasts (next", n_ahead, "periods):\\n")
for(i in 1:n_ahead) {{
    ci_lower <- forecasts[i] - 1.96 * fc$SDForecasts[i]
    ci_upper <- forecasts[i] + 1.96 * fc$SDForecasts[i]
    cat(sprintf("  Period %d: %.2f [%.2f, %.2f]\\n", i, forecasts[i], ci_lower, ci_upper))
}}

# Output JSON for Python parsing
output <- list(
    d = result$dHat,
    lambda = result$lambdaHat,
    sigma2 = result$sigma2Hat,
    phi = result$phiHat,
    theta = result$thetaHat,
    LL = result$LL,
    aic = result$aic,
    bic = result$bic,
    forecasts = forecasts,
    forecast_sd = fc$SDForecasts
)

cat("\\n__JSON_OUTPUT__\\n")
cat(jsonlite::toJSON(output, auto_unbox=TRUE))
cat("\\n__END_JSON__\\n")
'''
    return r_script

def run_r_artfima(z, p=3, q=11, glp="ARTFIMA"):
    """Run R ARTFIMA implementation"""
    # Save data to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df = pd.DataFrame({'co2': z})
        df.to_csv(f.name, index=False)
        data_file = f.name.replace('\\', '/')

    # Create R script
    r_script = create_r_script(data_file, p, q, glp)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.R', delete=False) as f:
        f.write(r_script)
        script_file = f.name

    try:
        # Run R script - use full path on Windows
        rscript_path = r'C:\Program Files\R\R-4.5.2\bin\Rscript.exe'
        if not os.path.exists(rscript_path):
            # Fallback to just 'Rscript' if full path doesn't exist
            rscript_path = 'Rscript'

        result = subprocess.run(
            [rscript_path, script_file],
            capture_output=True,
            text=True,
            timeout=120
        )

        print(result.stdout)

        if result.returncode != 0:
            print(f"R Error: {result.stderr}")
            return None

        # Parse JSON output
        output = result.stdout
        if "__JSON_OUTPUT__" in output:
            json_str = output.split("__JSON_OUTPUT__")[1].split("__END_JSON__")[0].strip()
            return json.loads(json_str)

        return None

    except subprocess.TimeoutExpired:
        print("R script timed out")
        return None
    except FileNotFoundError:
        print("Rscript not found - R may not be installed or not in PATH")
        return None
    finally:
        # Cleanup
        os.unlink(data_file)
        os.unlink(script_file)

def compare_results(python_result, r_result):
    """Compare Python and R results"""
    print("\n" + "="*60)
    print("COMPARISON: Python vs R")
    print("="*60)

    if r_result is None:
        print("R result not available - cannot compare")
        return

    comparisons = [
        ("d (fractional diff)", python_result['d'], r_result['d']),
        ("lambda (tempering)", python_result['lambda'], r_result['lambda']),
        ("sigma2 (variance)", python_result['sigma2'], r_result['sigma2']),
        ("Log-likelihood", python_result['LL'], r_result['LL']),
        ("AIC", python_result['aic'], r_result['aic']),
        ("BIC", python_result['bic'], r_result['bic']),
    ]

    print(f"\n{'Parameter':<25} {'Python':>15} {'R':>15} {'Diff':>15} {'Match':>10}")
    print("-" * 80)

    all_match = True
    for name, py_val, r_val in comparisons:
        diff = abs(py_val - r_val)
        match = diff < 0.01  # Allow small tolerance
        all_match = all_match and match
        status = "YES" if match else "NO"
        print(f"{name:<25} {py_val:>15.6f} {r_val:>15.6f} {diff:>15.6f} {status:>10}")

    # Compare forecasts
    print("\nForecast Comparison:")
    print(f"{'Period':<10} {'Python':>12} {'R':>12} {'Diff':>12} {'Match':>10}")
    print("-" * 60)

    for i, (py_fc, r_fc) in enumerate(zip(python_result['forecasts'], r_result['forecasts'])):
        diff = abs(py_fc - r_fc)
        match = diff < 0.1  # Allow small tolerance for forecasts
        all_match = all_match and match
        status = "YES" if match else "NO"
        print(f"{i+1:<10} {py_fc:>12.2f} {r_fc:>12.2f} {diff:>12.4f} {status:>10}")

    print("\n" + "="*60)
    if all_match:
        print("RESULT: Python and R implementations MATCH!")
    else:
        print("RESULT: There are DIFFERENCES between Python and R")
    print("="*60)

def main():
    print("ARTFIMA: Python vs R Comparison")
    print("Parameters: p=3, q=11, glp=ARTFIMA")
    print("Data: CO2 levels (monthly)")

    # Load data
    z = load_co2_data()

    # Run Python implementation
    python_result = run_python_artfima(z, p=3, q=11, glp="ARTFIMA")

    # Run R implementation
    print("\nRunning R implementation...")
    r_result = run_r_artfima(z, p=3, q=11, glp="ARTFIMA")

    # Compare
    compare_results(python_result, r_result)

if __name__ == "__main__":
    main()
