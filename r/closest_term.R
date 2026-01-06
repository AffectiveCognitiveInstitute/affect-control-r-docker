#!/usr/bin/env Rscript
# closest_term.R - Find closest dictionary term to an EPA vector

suppressPackageStartupMessages({
    library(jsonlite)
    library(actdata)
})

input <- tryCatch(fromJSON(file("stdin"), flatten = TRUE), error = function(e) list())

target_epa <- as.numeric(input$epa)
dictionary_key <- input$dictionary %||% "us2010"
component_type <- tolower(input$type %||% "identity")
n_results <- input$n %||% 5

if (length(target_epa) != 3) {
    write(toJSON(list(error = "epa must be [E, P, A] array"), auto_unbox = TRUE), stdout())
    quit(status = 0)
}

# Load dictionary
df <- actdata::epa_subset(dataset = dictionary_key)

if (!is.data.frame(df) || nrow(df) == 0) {
    write(toJSON(list(error = paste("Dictionary not found:", dictionary_key)), auto_unbox = TRUE), stdout())
    quit(status = 0)
}

# Filter by component type
if (!is.null(component_type) && component_type != "") {
    df <- subset(df, tolower(component) == component_type)
}

if (nrow(df) == 0) {
    write(toJSON(list(error = paste("No terms found for type:", component_type)), auto_unbox = TRUE), stdout())
    quit(status = 0)
}

# Calculate Euclidean distance for each term
df$distance <- sqrt(
    (df$E - target_epa[1])^2 + 
    (df$P - target_epa[2])^2 + 
    (df$A - target_epa[3])^2
)

# Sort by distance and get top N unique terms
df <- df[order(df$distance), ]
# Get unique terms (some terms appear multiple times for different groups)
unique_terms <- !duplicated(df$term)
df_unique <- df[unique_terms, ]
top_n <- head(df_unique, n_results)

matches <- lapply(1:nrow(top_n), function(i) {
    list(
        term = top_n$term[i],
        epa = c(round(top_n$E[i], 3), round(top_n$P[i], 3), round(top_n$A[i], 3)),
        distance = round(top_n$distance[i], 4),
        component = top_n$component[i]
    )
})

result <- list(
    target_epa = target_epa,
    dictionary = dictionary_key,
    type = component_type,
    matches = matches
)

write(toJSON(result, auto_unbox = TRUE), stdout())
