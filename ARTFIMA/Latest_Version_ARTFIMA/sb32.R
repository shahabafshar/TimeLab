# 
# Analysis of sb32 time series
# Figure 1 in the ARTFIMAfit paper
#
library(stats)

setwd("C:/Users/mcubed/Documents/research/hydro")
X=read.table('2009-2010-sb32velEcol1.txt',head=T)
x=as.ts(X)
#
# A few simple tests to make sure this worked
#
length(x)
mean(x)
var(x)
x[1]
#
# Begin exploratory data analysis
#
plot(x,type='l')
t=seq(1,300)
plot(x[t],type='l')
#
# plot of entire data set looks like noise.  Subplot shows structure. 
#
hist(x,freq=FALSE,xlab="sb32",main=NULL)
#
acf(x)
pacf(x)
#
# acf looks bit like LRD.  pacf oscillates to zero fairly quickly
#
#
require("artfima")
out <- artfima(x, likAlg="Whittle",fixd=5/6)
#
#ARTFIMA(0,0,0), MLE Algorithm: Whittle, optim: Brent
#snr = 4.364, sigmaSq = 3.5721692883066
#log-likelihood = -11045.19, AIC = 22098.37, BIC = 22124.73
#              est.    se(est.)
#mean   -0.55559278 0.084452517
#d       0.83333333 0.000000000
#lambda  0.04506006 0.003509009
#
# Plot periodogram and model spectral density
# This is Figure 1 in the ARTFIMAfit paper
#
sigmaSq0 <- out$sigmaSq
w <- x
n <- length(w)
Ip <- Periodogram(w)
fr <- (1/n)*(1:length(Ip))
plot(log(fr), log(Ip), xlab="log frequency", ylab="log power",
type="p", pch=16, cex=.4, ylim=c(-8,10))
y0 <- sigmaSq0*artfimaSDF(n=length(w), obj=out, plot="none")
lines(log(fr), log(y0), type="l", lwd=3.5, lty=1)
yK <- sigmaSq0*artfimaSDF(n=length(w), plot="none",
d=5/6,lambda=numeric(0))
lines(log(fr), log(yK), type="l", lwd=3.5, lty=2)
#
# Now let code also fit d
#
require("artfima")
out <- artfima(x, likAlg="Whittle")
#
#ARTFIMA(0,0,0), MLE Algorithm: Whittle, optim: BFGS
#snr = 4.407, sigmaSq = 3.54434450893359
#log-likelihood = -11024.17, AIC = 22056.33, BIC = 22082.69
#             est.    se(est.)
#mean   -0.55559278 0.084452423
#d       0.75228378 0.008237452
#lambda  0.02652803 0.003237423
#
# Plot periodogram and model spectral density
#
#sigmaSq0 <- out$sigmaSq
#w <- x
#n <- length(w)
#Ip <- Periodogram(w)
#fr <- (1/n)*(1:length(Ip))
#plot(log(fr), log(Ip), xlab="log frequency", ylab="log power",
#type="p", pch=16)
#y0 <- sigmaSq0*artfimaSDF(n=length(w), obj=out, plot="none")
#lines(log(fr), log(y0), type="l", lwd=3.5, lty=2)
#
# Plot periodogram and model spectral density
#
#sigmaSq0 <- out$sigmaSq
#w <- x
#n <- length(w)
#Ip <- Periodogram(w)
#fr <- (1/n)*(1:length(Ip))
#plot(log(fr), log(Ip), xlab="log frequency", ylab="log power",
#type="p", pch=16)
#y0 <- sigmaSq0*artfimaSDF(n=length(w), obj=out, plot="none")
#lines(log(fr), log(y0), type="l", lwd=3.5, lty=2)


