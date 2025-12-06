# R script to generate 24-period ARTFIMA forecasts
library(artfima)

# Load data
data <- read.csv('backend/data/samples/co2_levels.csv')
z <- data$co2
z_diff <- diff(z)

cat('Data length:', length(z_diff), '\n')
cat('Last CO2 value:', tail(z, 1), '\n\n')

# Fit ARTFIMA(3,d,11)
cat('Fitting ARTFIMA(3,d,11)...\n')
fit <- artfima(z_diff, glp='ARTFIMA', arimaOrder=c(3,0,11))

cat('\nR Model Results:\n')
cat('  d =', fit$dHat, '\n')
cat('  lambda =', fit$lambdaHat, '\n')
cat('  LL =', fit$LL, '\n')
cat('  AIC =', fit$aic, '\n\n')

# Generate 24-period forecasts
cat('Generating 24-period forecasts...\n')
fc <- predict(fit, n.ahead=24)

cat('\nR 24-Period Forecasts (centered):\n')
print(fc$pred)

# Convert to level forecasts
fc_pred <- fc$pred
fc_level <- numeric(24)
last_level <- tail(z, 1)
mean_diff <- mean(z_diff)
for (i in 1:24) {
    fc_level[i] <- last_level + fc_pred[i] + mean_diff
    last_level <- fc_level[i]
}

cat('\nR 24-Period Level Forecasts:\n')
for (i in 1:24) {
    cat(sprintf('h=%2d: %.2f\n', i, fc_level[i]))
}

cat('\nSummary:\n')
cat('  First forecast (h=1):', round(fc_level[1], 2), '\n')
cat('  Last forecast (h=24):', round(fc_level[24], 2), '\n')
cat('  Range: [', round(min(fc_level), 2), ',', round(max(fc_level), 2), ']\n')
