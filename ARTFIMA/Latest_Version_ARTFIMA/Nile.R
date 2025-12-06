require("artfima")
data(nilemin)
artfima(nilemin, likAlg="Whittle")
artfima(nilemin, likAlg="Whittle", glp="ARFIMA")
## Not run:
#compare exact and Whittle using bestModel()
start <- proc.time()[3]
ans<-bestModel(nilemin)
tot <- proc.time()[3]-start
start <- proc.time()[3]
ansW <- bestModel(nilemin, likAlg="Whittle")
totW <- proc.time()[3]-start
t <- c(tot, totW)
names(t) <- c("exact", "Whittle")
#compare times - about 100 seconds vs 3 seconds
t
#compare best models
ans
ansW
#AIC/BIC scores similar but rankings to change.
#ARTFIMA(0,0,0) is ranked best by both AIC and BIC
#ARIMA(2,0,1) is ranked second best by both AIC and BIC
#ARFIMA(0,0,0) is ranked 3rd by BIC and is not among top 5 by AIC
## End(Not run)