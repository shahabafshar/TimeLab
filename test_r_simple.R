# Simple R ARTFIMA comparison
library(artfima)
library(ltsa)

# Load data
data <- read.csv('backend/data/samples/co2_levels.csv')
z <- data$co2
z_diff <- diff(z)
n <- length(z_diff)
mean_diff <- mean(z_diff)

cat(strrep('=', 70), '\n')
cat('R ARTFIMA(3,d,11) - 24 Period Forecast Comparison\n')
cat(strrep('=', 70), '\n\n')

cat('Data length:', n, '\n')
cat('Last CO2 value:', tail(z, 1), '\n\n')

# Fit model
fit <- artfima(z_diff, glp='ARTFIMA', arimaOrder=c(3,0,11))

cat('R Model Results:\n')
cat('  d =', fit$dHat, '\n')
cat('  lambda =', fit$lambdaHat, '\n')
cat('  LL =', fit$LL, '\n')
cat('  AIC =', fit$aic, '\n')
cat('  sigmaSq =', fit$sigmaSq, '\n')
cat('  phi =', fit$phiHat, '\n')
cat('  theta =', fit$thetaHat, '\n\n')

# Generate forecasts using TrenchForecast directly
h <- 24
r <- artfimaTACVF(maxlag=n+h, obj=fit)
zm <- fit$constant

cat('Generating 24-period forecasts...\n')
fc <- TrenchForecast(z_diff, r, zm, n, maxLead=h)

cat('\nR 24-Period Forecasts:\n')
cat(strrep('-', 50), '\n')
cat(sprintf('%-8s %-15s %-15s\n', 'Period', 'Diff Forecast', 'Level Forecast'))
cat(strrep('-', 50), '\n')

fc_level <- numeric(h)
last_level <- tail(z, 1)

for (i in 1:h) {
    fc_diff <- fc$Forecast[i]
    fc_level[i] <- last_level + fc_diff + mean_diff
    last_level <- fc_level[i]
    cat(sprintf('%-8d %12.4f   %12.2f\n', i, fc_diff, fc_level[i]))
}

cat('\n')
cat(strrep('=', 70), '\n')
cat('SUMMARY\n')
cat(strrep('=', 70), '\n')
cat('  First forecast (h=1):', round(fc_level[1], 2), '\n')
cat('  Last forecast (h=24):', round(fc_level[h], 2), '\n')
cat('  Range: [', round(min(fc_level), 2), ',', round(max(fc_level), 2), ']\n')
