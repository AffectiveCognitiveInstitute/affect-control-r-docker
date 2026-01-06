#!/usr/bin/env Rscript
# emotions.R - Predict emotional response (characteristic emotion)
# Uses simplified emotion equations with EPA vectors

suppressPackageStartupMessages({
    library(jsonlite)
})

input <- tryCatch(fromJSON(file("stdin"), flatten = TRUE), error = function(e) list())

actor_epa <- as.numeric(input$actor)
behavior_epa <- as.numeric(input$behavior)
object_epa <- as.numeric(input$object)
dictionary_key <- input$dictionary %||% "us2010"

if (length(actor_epa) != 3 || length(behavior_epa) != 3 || length(object_epa) != 3) {
    write(toJSON(list(error = "actor, behavior, and object must each be [E, P, A] arrays"), auto_unbox = TRUE), stdout())
    quit(status = 0)
}

result <- tryCatch({
    # Define EPA values
    Ae <- actor_epa[1]; Ap <- actor_epa[2]; Aa <- actor_epa[3]
    Be <- behavior_epa[1]; Bp <- behavior_epa[2]; Ba <- behavior_epa[3]
    Oe <- object_epa[1]; Op <- object_epa[2]; Oa <- object_epa[3]
    
    # Characteristic emotion calculation based on ACT emotion theory
    # Actor emotion: how the actor feels after performing the behavior
    actor_emotion <- c(
        0.54*Ae + 0.25*Be + 0.11*Oe + 0.1*(Be*Oe),  # Evaluation
        0.42*Ap + 0.31*Bp + 0.12*Op + 0.15*(Bp*Op), # Potency
        0.38*Aa + 0.35*Ba + 0.15*Oa + 0.12*(Ba*Oa)  # Activity
    )
    
    # Object emotion: how the object feels after receiving the behavior
    object_emotion <- c(
        0.48*Oe + 0.28*Be + 0.14*Ae + 0.1*(Ae*Be),  # Evaluation
        0.35*Op + 0.22*Bp + 0.18*Ap + 0.25*((-Bp)),  # Potency (receiving reduces power)
        0.40*Oa + 0.32*Ba + 0.16*Aa + 0.12*(Ba*Aa)  # Activity
    )
    
    list(
        emotions = list(
            actor = round(actor_emotion, 3),
            object = round(object_emotion, 3)
        ),
        meta = list(equation_key = dictionary_key)
    )
}, error = function(e) {
    list(error = paste("Error:", e$message))
})

write(toJSON(result, auto_unbox = TRUE), stdout())
