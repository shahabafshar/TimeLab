# fit ARTFIMA to ln K data at MADE site borehole A121108
#
setwd("C:/Users/mcubed/Documents/research/Farzad")
X=read.table('A121108lnK.txt',head=F)
xt=X[,1]
#
require("artfima")
#
out <- artfima(xt, arimaOrder=c(0,0,0), likAlg="Whittle")
out
#
#res=out$res
#acf(res)
#
# plot spectral density, visual check for power law fit
#
n=length(xt)
sigmaSq0 <- out$sigmaSq
Ip<- Periodogram(xt) 
fr <- (1/n)*(1:length(Ip))
plot(log(fr), log(Ip/3.14159), xlab="log frequency", ylab="log power",
type="p",pch=16, cex=.5)
y0 <- sigmaSq0*artfimaSDF(n=length(xt), obj=out, plot="none")
lines(log(fr), log(y0), type="l", lwd=3.5, lty=1)
#
# ARFIMA plot invisible, right over ARTFIMA
#
#D=out$d
#y1 <- sigmaSq0*artfimaSDF(n=length(xt), d=D, plot="none",
#lambda=numeric(0))
#lines(log(fr), log(y1), type="l", lwd=3.5, lty=2)






