"""
Compare TACVF and likelihood calculations between Python and R at identical parameters
"""
import sys
import os
import numpy as np
import pandas as pd
from pathlib import Path
import tempfile
import subprocess

# Add ARTFIMA package to path
artfima_path = Path(__file__).parent / "ARTFIMA"
if str(artfima_path) not in sys.path:
    sys.path.insert(0, str(artfima_path))

from artfima_python.tacvf import artfimaTACVF
from artfima_python.durbin_levinson import DLLoglikelihood

# Load data
data_path = Path(__file__).parent / "backend" / "data" / "samples" / "co2_levels.csv"
df = pd.read_csv(data_path)
z = df['co2'].values
z_diff = np.diff(z)
w = z_diff - np.mean(z_diff)  # Center data

print(f"Data: {len(z_diff)} observations (differenced)")
print(f"Variance: {np.var(w):.6f}")

# Test parameters - use BOTH Python's optimum AND R's optimum
test_cases = [
    {
        "name": "Python optimum",
        "d": -0.132560,
        "lambda": 1.592113,
        "phi": np.array([-0.24596835, 0.34883223, 0.89825193]),
        "theta": np.array([-0.49831403, -0.30462541, 0.6024325, 0.28067032, 0.7865927,
                          0.89501841, 0.3108201, 0.0486347, -0.5184478, -0.28722408, -0.40020721])
    },
    {
        "name": "R optimum",
        "d": 9.999682,
        "lambda": 2.021603,
        "phi": np.array([-1.692132, -0.6944333, 0.08887375]),
        "theta": np.array([-0.2645191, 0.7208977, 0.02223315, 0.2195057, 0.5952384,
                          0.1984419, 0.1996436, -0.03327467, -0.1814059, -0.3054669, -0.2574475])
    },
    {
        "name": "Simple test (d=0.3, lambda=0.5)",
        "d": 0.3,
        "lambda": 0.5,
        "phi": np.array([0.1]),
        "theta": np.array([0.3])
    }
]

print("\n" + "="*70)
print("PYTHON TACVF AND LIKELIHOOD CALCULATIONS")
print("="*70)

for case in test_cases:
    print(f"\n--- {case['name']} ---")
    print(f"d={case['d']}, lambda={case['lambda']}")
    print(f"phi={case['phi'][:3]}...")
    print(f"theta={case['theta'][:3]}...")

    try:
        tacvf = artfimaTACVF(
            d=case['d'],
            lambda_param=case['lambda'],
            phi=case['phi'],
            theta=case['theta'],
            maxlag=len(w)-1
        )

        if np.all(np.isfinite(tacvf)):
            ll = DLLoglikelihood(tacvf, w)
            n = len(w)
            k = 2 + len(case['phi']) + len(case['theta'])  # d, lambda, phi, theta
            aic = -2 * ll + 2 * k

            print(f"TACVF[0:5]: {tacvf[:5]}")
            print(f"Log-likelihood: {ll:.4f}")
            print(f"AIC: {aic:.4f}")
        else:
            print("TACVF contains non-finite values!")
            print(f"Non-finite count: {np.sum(~np.isfinite(tacvf))}")
    except Exception as e:
        print(f"Error: {e}")

# Now run R to compute the same values
print("\n" + "="*70)
print("R TACVF AND LIKELIHOOD CALCULATIONS")
print("="*70)

# Create R script to compute TACVF at Python's parameters
artfima_r_path = str(Path(__file__).parent / "ARTFIMA" / "artfima" / "R").replace('\\', '/')
data_file = str(data_path).replace('\\', '/')

r_script = f'''
library(gsl)
library(ltsa)

# Source artfima R files
artfima_path <- "{artfima_r_path}"
r_files <- c("artfimaTACVF.R", "ifisher.R", "InvertibleQ.R")
for(f in r_files) {{
    source(file.path(artfima_path, f))
}}

# Load and prepare data
data <- read.csv("{data_file}")
z <- data$co2
z_diff <- diff(z)
w <- z_diff - mean(z_diff)
n <- length(w)

cat("Data:", n, "observations (differenced)\\n")
cat("Variance:", var(w), "\\n")

# Test case 1: Python optimum
cat("\\n--- Python optimum ---\\n")
d1 <- -0.132560
lambda1 <- 1.592113
phi1 <- c(-0.24596835, 0.34883223, 0.89825193)
theta1 <- c(-0.49831403, -0.30462541, 0.6024325, 0.28067032, 0.7865927,
            0.89501841, 0.3108201, 0.0486347, -0.5184478, -0.28722408, -0.40020721)

tacvf1 <- artfimaTACVF(d=d1, lambda=lambda1, phi=phi1, theta=theta1, maxlag=n-1)
cat("TACVF[1:5]:", tacvf1[1:5], "\\n")

# Compute log-likelihood using Durbin-Levinson
DLLoglikelihood <- function(r, z) {{
    n <- length(z)
    L <- TrenchLoglikelihood(r, z)
    return(L)
}}

ll1 <- DLLoglikelihood(tacvf1, w)
k1 <- 2 + length(phi1) + length(theta1)
aic1 <- -2 * ll1 + 2 * k1
cat("Log-likelihood:", ll1, "\\n")
cat("AIC:", aic1, "\\n")

# Test case 2: R optimum
cat("\\n--- R optimum ---\\n")
d2 <- 9.999682
lambda2 <- 2.021603
phi2 <- c(-1.692132, -0.6944333, 0.08887375)
theta2 <- c(-0.2645191, 0.7208977, 0.02223315, 0.2195057, 0.5952384,
            0.1984419, 0.1996436, -0.03327467, -0.1814059, -0.3054669, -0.2574475)

tacvf2 <- artfimaTACVF(d=d2, lambda=lambda2, phi=phi2, theta=theta2, maxlag=n-1)
cat("TACVF[1:5]:", tacvf2[1:5], "\\n")

ll2 <- DLLoglikelihood(tacvf2, w)
k2 <- 2 + length(phi2) + length(theta2)
aic2 <- -2 * ll2 + 2 * k2
cat("Log-likelihood:", ll2, "\\n")
cat("AIC:", aic2, "\\n")

# Test case 3: Simple test
cat("\\n--- Simple test (d=0.3, lambda=0.5) ---\\n")
d3 <- 0.3
lambda3 <- 0.5
phi3 <- c(0.1)
theta3 <- c(0.3)

tacvf3 <- artfimaTACVF(d=d3, lambda=lambda3, phi=phi3, theta=theta3, maxlag=n-1)
cat("TACVF[1:5]:", tacvf3[1:5], "\\n")

ll3 <- DLLoglikelihood(tacvf3, w)
k3 <- 2 + length(phi3) + length(theta3)
aic3 <- -2 * ll3 + 2 * k3
cat("Log-likelihood:", ll3, "\\n")
cat("AIC:", aic3, "\\n")
'''

with tempfile.NamedTemporaryFile(mode='w', suffix='.R', delete=False) as f:
    f.write(r_script)
    script_file = f.name

try:
    rscript_path = r'C:\Program Files\R\R-4.5.2\bin\Rscript.exe'
    result = subprocess.run(
        [rscript_path, script_file],
        capture_output=True,
        text=True,
        timeout=60
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
finally:
    os.unlink(script_file)
