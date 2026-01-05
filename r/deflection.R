#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(jsonlite)
})

# Read input
input <- fromJSON(file("stdin"), flatten = TRUE)

# Input:
# {
#   "fundamental": { "actor": [E,P,A], "behavior": [E,P,A], "object": [E,P,A] },
#   "transient": { "actor": [E,P,A], "behavior": [E,P,A], "object": [E,P,A] },
#   "weights": { "actor": [wE,wP,wA], ... } (Optional)
# }

compute_deflection <- function(inp) {
  f <- inp$fundamental
  t <- inp$transient
  
  # Helper to safe convert to numeric
  get_epa <- function(x) as.numeric(x)
  
  ae_sq <- sum((get_epa(f$actor) - get_epa(t$actor))^2)
  be_sq <- sum((get_epa(f$behavior) - get_epa(t$behavior))^2)
  oe_sq <- sum((get_epa(f$object) - get_epa(t$object))^2)
  
  # Standard deflection is sum of squared differences
  total_deflection <- ae_sq + be_sq + oe_sq
  
  return(list(
    deflection = total_deflection,
    components = list(actor = ae_sq, behavior = be_sq, object = oe_sq)
  ))
}

result <- tryCatch({
  compute_deflection(input)
}, error = function(e) {
  list(error = e$message)
})

write(toJSON(result, auto_unbox = TRUE), stdout())
