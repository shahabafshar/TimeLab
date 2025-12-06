# Illustrate ACF 
#
require("artfima")
#
# linear plot vary lambda 
#
m=30
lag=seq(1,m+1)
ACF=lag
lambda = 0.0
d = .4
ACVF = artfimaTACVF(d=d, lambda=lambda, maxlag=m)
for (j in 1:m+1){ACF[j]=ACVF[j]/ACVF[1]}
plot(lag, ACF, type="l",ylim=c(0,1))
lambda = .001
ACVF = artfimaTACVF(d=d, lambda=lambda, maxlag=m)
for (j in 1:m+1){ACF[j]=ACVF[j]/ACVF[1]}
lines((lag), (ACF), type="l")
lambda = .05
ACVF = artfimaTACVF(d=d, lambda=lambda, maxlag=m)
for (j in 1:m+1){ACF[j]=ACVF[j]/ACVF[1]}
lines((lag), (ACF), type="l")
lambda = .1
ACVF = artfimaTACVF(d=d, lambda=lambda, maxlag=m)
for (j in 1:m+1){ACF[j]=ACVF[j]/ACVF[1]}
lines((lag), (ACF), type="l")
#
# linear plot vary d 
#
m=30
lag=seq(1,m+1)
ACF=lag
lambda = .1
d = .3
ACVF = artfimaTACVF(d=d, lambda=lambda, maxlag=m)
for (j in 1:m+1){ACF[j]=ACVF[j]/ACVF[1]}
plot(lag, ACF, type="l",ylim=c(0,1))
d = .6
ACVF = artfimaTACVF(d=d, lambda=lambda, maxlag=m)
for (j in 1:m+1){ACF[j]=ACVF[j]/ACVF[1]}
lines((lag), (ACF), type="l")
d = .9
ACVF = artfimaTACVF(d=d, lambda=lambda, maxlag=m)
for (j in 1:m+1){ACF[j]=ACVF[j]/ACVF[1]}
lines((lag), (ACF), type="l")
d = 1.2
ACVF = artfimaTACVF(d=d, lambda=lambda, maxlag=m)
for (j in 1:m+1){ACF[j]=ACVF[j]/ACVF[1]}
lines((lag), (ACF), type="l")





