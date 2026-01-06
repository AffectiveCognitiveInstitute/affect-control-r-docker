#!/usr/bin/env Rscript
# transients.R - Calculate transient impressions after an event
# Uses simplified impression formation equations with EPA vectors

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
    
    # Transient impression calculation based on ACT impression formation
    # Simplified coefficients based on standard ACT equations
    # Actor transient: influenced by own identity + behavior toward object
    actor_trans <- c(
        0.616*Ae + 0.221*Be + 0.077*Oe + 0.086*Be*Oe,
        0.528*Ap + 0.296*Bp + 0.083*Op + 0.093*Bp*Op,
        0.597*Aa + 0.159*Ba + 0.115*Oa + 0.129*Ba*Oa
    )
    
    # Behavior transient: influenced by actor doing it to object
    behavior_trans <- c(
        0.158*Ae + 0.521*Be + 0.182*Oe + 0.139*Ae*Oe,
        0.103*Ap + 0.538*Bp + 0.198*Op + 0.161*Ap*Op,
        0.117*Aa + 0.542*Ba + 0.163*Oa + 0.178*Aa*Oa
    )
    
    # Object transient: influenced by receiving behavior from actor
    object_trans <- c(
        0.081*Ae + 0.189*Be + 0.637*Oe + 0.093*Ae*Be,
        0.072*Ap + 0.229*Bp + 0.564*Op + 0.135*Ap*Bp,
        0.099*Aa + 0.168*Ba + 0.618*Oa + 0.115*Aa*Ba
    )
    
    list(
        transients = list(
            actor = round(actor_trans, 3),
            behavior = round(behavior_trans, 3),
            object = round(object_trans, 3)
        ),
        meta = list(equation_key = dictionary_key)
    )
}, error = function(e) {
    list(error = paste("Error:", e$message))
})

write(toJSON(result, auto_unbox = TRUE), stdout())
