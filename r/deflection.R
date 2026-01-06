#!/usr/bin/env Rscript
# deflection.R - Calculate deflection between fundamental and transient EPAs

suppressPackageStartupMessages({
    library(jsonlite)
})

input <- tryCatch(fromJSON(file("stdin"), flatten = TRUE), error = function(e) list())

fundamentals <- input$fundamentals
transients <- input$transients

if (is.null(fundamentals) || is.null(transients)) {
    write(toJSON(list(error = "Both 'fundamentals' and 'transients' are required"), auto_unbox = TRUE), stdout())
    quit(status = 0)
}

# Extract EPA vectors - expecting lists with A, B, O keys each containing [E, P, A]
calc_element_deflection <- function(fund, trans) {
    if (is.null(fund) || is.null(trans)) return(0)
    fund <- as.numeric(fund)
    trans <- as.numeric(trans)
    if (length(fund) != 3 || length(trans) != 3) return(0)
    sum((fund - trans)^2)
}

actor_deflection <- calc_element_deflection(fundamentals$actor, transients$actor)
behavior_deflection <- calc_element_deflection(fundamentals$behavior, transients$behavior)
object_deflection <- calc_element_deflection(fundamentals$object, transients$object)

total_deflection <- actor_deflection + behavior_deflection + object_deflection

result <- list(
    deflection = list(
        total = round(total_deflection, 4),
        actor = round(actor_deflection, 4),
        behavior = round(behavior_deflection, 4),
        object = round(object_deflection, 4)
    )
)

write(toJSON(result, auto_unbox = TRUE), stdout())
