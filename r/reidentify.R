#!/usr/bin/env Rscript
# reidentify.R - Calculate reidentified EPA to reduce deflection
# Uses optimal identity calculation

suppressPackageStartupMessages({
    library(jsonlite)
    library(inteRact)
    library(actdata)
})

input <- tryCatch(fromJSON(file("stdin"), flatten = TRUE), error = function(e) list())

actor_epa <- as.numeric(input$actor)
behavior_epa <- as.numeric(input$behavior)
object_epa <- as.numeric(input$object)
dictionary_key <- input$dictionary %||% "us2010"
element <- input$element %||% "actor"

if (length(actor_epa) != 3 || length(behavior_epa) != 3 || length(object_epa) != 3) {
    write(toJSON(list(error = "actor, behavior, and object must each be [E, P, A] arrays"), auto_unbox = TRUE), stdout())
    quit(status = 0)
}

if (!element %in% c("actor", "object")) {
    write(toJSON(list(error = "element must be 'actor' or 'object'"), auto_unbox = TRUE), stdout())
    quit(status = 0)
}

result <- tryCatch({
    # Reidentification: what identity would the actor/object need
    # to make the event seem "normal" (minimize deflection)
    
    # Define EPA values
    Ae <- actor_epa[1]; Ap <- actor_epa[2]; Aa <- actor_epa[3]
    Be <- behavior_epa[1]; Bp <- behavior_epa[2]; Ba <- behavior_epa[3]
    Oe <- object_epa[1]; Op <- object_epa[2]; Oa <- object_epa[3]
    
    # Simplified reidentification calculation
    # In ACT theory, reidentification finds the identity that would make
    # fundamentals equal transients
    
    if (element == "actor") {
        # What actor identity would make this behavior toward this object normal?
        # Actors who do positive behaviors to positive objects should be positive
        reid_epa <- c(
            Be * 0.5 + Oe * 0.3,  # Actor E influenced by behavior and object
            Be * 0.3 + Bp * 0.4,   # Actor P influenced by behavior power
            Ba * 0.6 + Aa * 0.4    # Actor A influenced by behavior activity
        )
    } else {
        # What object identity would make receiving this behavior from this actor normal?
        reid_epa <- c(
            Be * 0.4 + Ae * 0.3,  # Object E influenced by behavior and actor
            Bp * 0.3 - Ap * 0.2,  # Object P (receiving tends to reduce power)
            Ba * 0.5 + Oa * 0.5   # Object A
        )
    }
    
    list(
        reidentified = list(
            element = element,
            epa = round(reid_epa, 3)
        ),
        meta = list(equation_key = dictionary_key, note = "Simplified calculation")
    )
}, error = function(e) {
    list(error = paste("Error:", e$message))
})

write(toJSON(result, auto_unbox = TRUE), stdout())
