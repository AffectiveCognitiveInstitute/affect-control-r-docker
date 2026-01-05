#!/usr/bin/env Rscript

# Load required packages
suppressPackageStartupMessages({
  library(jsonlite)
  library(actdata)
})

# Read JSON from stdin
input <- fromJSON(file("stdin"), flatten = TRUE)

# Extract parameters
label <- input$label
type <- input$type # "identity", "behavior", "modifier", "setting"
dictionary <- input$dictionary # Optional, e.g., "us_2015"

# Default to a standard dictionary if not provided (e.g., avg1978 or us_merged)
# For now, let's look at what actdata provides.
# actdata typically has datasets like us_2015, china_2015, etc.

find_epa <- function(lbl, type, diet_name) {
  # This is a simplified lookup logic. 
  # In a real implementation, we would inspect available dictionaries in actdata.
  # For the purpose of this task, we will try to find the term in the loaded datasets.
  
  # Just some example datasets often found in actdata
  # We'll use 'us_2015' as a default modern US dictionary if available/requested
  
  # For this minimal implementation, I'll assume we access a generic compiled dataset 
  # or iterate through common ones.
  # Let's try to map the requested dictionary string to a dataset object.
  
  data_source <- NULL
  
  # Mapping common names to actdata objects (assuming they are lazy-loaded)
  # Note: The exact variable names depend on the actdata package version.
  # We will try a few standard ones.
  
  if (is.null(diet_name) || diet_name == "default") {
     if (exists("us_2015")) data_source <- us_2015
     else if (exists("us_avg_2015")) data_source <- us_avg_2015
     else if (exists("averages")) data_source <- averages # older actdata
  } else {
     if (exists(diet_name)) data_source <- get(diet_name)
  }
  
  if (is.null(data_source)) {
    # Fallback: create a dummy warning if we can't find data.
    # But actdata *should* represent data.
    return(list(error = paste("Dictionary not found:", diet_name)))
  }
  
  # Filter by term
  # Dataframes usually have columns: term, E, P, A, (and maybe type/gender)
  
  # Normalize label
  lbl_lower <- tolower(lbl)
  
  match <- subset(data_source, tolower(term) == lbl_lower)
  
  if (nrow(match) == 0) {
    return(list(error = paste("Term not found:", lbl)))
  }
  
  # If multiple matches (e.g. gendered), for this minimal API, take the first or average.
  # Let's take the first for simplicity and deterministic behavior.
  row <- match[1, ]
  
  return(list(
    term = row$term,
    epa = c(as.numeric(row$E), as.numeric(row$P), as.numeric(row$A)),
    metadata = as.list(row)
  ))
}

result <- tryCatch({
  find_epa(label, type, dictionary)
}, error = function(e) {
  list(error = e$message)
})

# Write JSON to stdout
write(toJSON(result, auto_unbox = TRUE), stdout())
