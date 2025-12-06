# 
# Analysis of uv_32.mat time series
#
# Save data in MATLAB as earlier version using "save uv -V6"
#
# Read data from MATLAB file 
#
require(R.matlab)
setwd("C:/Documents and Settings/MCubed/My Documents/Research/turbulence")
data <- readMat("uv.mat")
#
# Can also read uv_32.txt instead (much slower)
#path='C:/Documents and Settings/MCubed/My Documents/Research/uv_32.txt'
#data=read.table(path,header=FALSE)
#
# Next convert data frame to a vector of values
# Query R to find data type (list) and name of variable (uv), then extract
#
class(data)
names(data)
x=data$uv
class(x)
x=as.ts(x)
#
# A few simple tests to make sure this worked
#
length(x)
mean(x)
var(x)
x[1]
#
#
start=1
len=10000
t=seq(1,len)
xt=x[t-1+start]
n=length(xt)
require("artfima")
out <- artfima(xt, arimaOrder=c(2,0,0))
out
#res=out$res
#acf(res)
#
# Output from artfima with start=1 and len=10000 ...
#
# ARTFIMA(2,0,0), MLE Algorithm: exact, optim: BFGS
# snr = 306.059, sigmaSq = 4.68879769956692e-05
# log-likelihood = 35645.62, AIC = -71279.24, BIC = -71235.98
#               est.    se(est.)
# mean   -0.01371198 0.001696857
# d       1.33538896 0.048606826
# lambda  0.05307105 0.006463144
# phi(1)  1.02572822 0.016379699
# phi(2) -0.44971282 0.015817899
#
# Plot the theoretical spectral density over the sample spectral density
#
sigmaSq0 <- out$sigmaSq
Ip<- Periodogram(xt) 
fr <- (1/n)*(1:length(Ip))
plot(log(fr), log(Ip), xlab="log frequency", ylab="log power",
type="p",pch=16, cex=.2)
y0 <- sigmaSq0*artfimaSDF(n=length(xt), obj=out, plot="none")
lines(log(fr), log(y0), type="l", lwd=3.5, lty=2)
#
# Plot averaged spectral density over sample spectral density
#
gap=1000
T=floor(length(x)/(len+gap)-start-1) # avoid overrunning end of sequence
Lp=length(Ip)
Per <- array(0,c(T,Lp)) 
for (i in 1:T){
w=x[t+(i-1)*(gap+start)]
Per[i,]<- Periodogram(w)}
Ip=colMeans(Per)
plot(log(fr), log(Ip), xlab="log frequency", ylab="log power",
type="p",pch=16, cex=.2,ylim=c(-14,0))
y0 <- sigmaSq0*artfimaSDF(n=length(w), obj=out, plot="none")
lines(log(fr), log(y0), type="l", lwd=3.5, lty=1)
# To use median instead of mean
# require(miscTools)  
# Ip=colMedians(Per) 
# plot(log(fr), log(Ip), xlab="log frequency", ylab="log power",
# type="p",pch=16, cex=.2,ylim=c(-14,0))
# y0 <- sigmaSq0*artfimaSDF(n=length(w), obj=out, plot="none")
# lines(log(fr), log(y0), type="l", lwd=3.5, lty=2)
#



