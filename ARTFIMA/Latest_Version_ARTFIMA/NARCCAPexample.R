# fit ARTFIMA to J. French data
setwd("C:/Users/mcubed/Documents/research/FRGpiotr")
X=read.table('r1.txt',head=T)
#
require("artfima")
#
out <- artfima(X[,1], likAlg="Whittle")
out
#
#res=out$res
#acf(res)
#
# plot spectral density, visual check for power law fit
#
sigmaSq0 <- out$sigmaSq
D=out$d
w <- X[,1]
n <- length(w)
Ip <- Periodogram(w)
fr <- (1/n)*(1:length(Ip))
plot(log(fr), log(Ip), xlab="log frequency", ylab="log power",
type="p", pch=16, cex=.4, ylim=c(-10,10))
y0 <- sigmaSq0*artfimaSDF(n=length(w), obj=out, plot="none")
lines(log(fr), log(y0), type="l", lwd=3.5, lty=1)
#
# Asymptote
#
#y1 <- sigmaSq0*artfimaSDF(n=length(w), d=D, plot="none",
#lambda=numeric(0))
#lines(log(fr), log(y1), type="l", lwd=3.5, lty=2)
#
# Try ARFIMA fit.  Difference first!
#
xt=diff(X[,1])
out <- artfima(xt, likAlg="Whittle", glp="ARFIMA")
out
res=out$res
acf(res)
#
# Compare to ARTFIMA applied to differenced data
#
out <- artfima(xt, likAlg="Whittle")
out#res=out$res
#acf(res)





