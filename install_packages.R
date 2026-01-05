# Install CRAN packages
install.packages(c("devtools", "remotes", "Rcpp", "jsonlite"), repos='http://cran.rstudio.com/')

# Install dependencies for inteRact and bayesactR
# Note: inteRact and actdata are on CRAN
install.packages("actdata", repos='http://cran.rstudio.com/')
install.packages("inteRact", repos='http://cran.rstudio.com/')

# Install bayesactR from GitHub
# Note: bayesactR might not be on CRAN, checking research
# Research indicated: "To install `bayesactR`, you would typically install it from GitHub."
# Research source: https://github.com/ahcombs/bayesactR
library(devtools)
install_github("ahcombs/bayesactR")

# Verify installation
library(actdata)
library(inteRact)
library(bayesactR)
print("All ACT packages loaded successfully")
