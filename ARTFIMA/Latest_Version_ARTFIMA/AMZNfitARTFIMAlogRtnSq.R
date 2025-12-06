# fit ARTFIMA to AMZN adjusted closing price 1/3/2000 to 12/19/2017
# squared log returns
#
setwd("C:/Users/mcubed/Documents/research/Farzad")
X=read.table('AMZNadjCloselogreturnsquared.txt',head=F)
xt=X[,1]
#
require("artfima")
#
out <- artfima(xt, arimaOrder=c(0,0,0), likAlg="Whittle")
out
#ARTFIMA(0,0,0), MLE Algorithm: Whittle, optim: L-BFGS-B
#snr = 0.006, sigmaSq = 1.78695616535146e-05
#log-likelihood = 18289.47, AIC = -36570.93, BIC = -36545.27
#              est.    se(est.)
#mean   0.001130145 8.91756e-05
#d      0.299992020          NA
#lambda 0.025000250          NA
#
# plot spectral density, visual check for power law fit
#
n=length(xt)
sigmaSq0 <- out$sigmaSq
#Ip<- spectrum(xt,plot=FALSE,spans=c(3,3)) 
#Ip<- spectrum(xt,plot=FALSE, kernel("daniell", c(3,3))) 
Ip<- spectrum(xt,plot=FALSE) 
fr <- Ip$freq
sp <- Ip$spec
plot(log(fr), log(sp), xlab="log frequency", ylab="log power",
type="p",pch=16, cex=.2, ylim=c(-20,-7))
y0 <- sigmaSq0*artfimaSDF(n=length(xt), obj=out, plot="none")
L=length(y0)-1
fr2=seq(0:L)/(2*length(y0))
lines(log(fr2), log(y0), type="l", lwd=3.5, lty=1)
#
# Add ARFIMA straight line
#
D=out$d
y1 <- sigmaSq0*artfimaSDF(n=length(xt), d=D, plot="none",
lambda=numeric(0))
lines(log(fr2), log(y1), type="l", lwd=3.5, lty=2)

