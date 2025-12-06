require("artfima")
setwd("C:/Users/mcubed/Documents/research/Farzad")
X=read.table('AMZNadjCloselogreturnsquared.txt',head=F)
xt=X[,1]
artfima(xt, likAlg="exact")
artfima(xt, likAlg="exact", glp="ARFIMA")
