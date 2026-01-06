#!/usr/bin/env Rscript

suppressPackageStartupMessages({
    library(jsonlite)
    library(inteRact)
})

`%||%` <- function(x, y) if (!is.null(x) && length(x) > 0) x else y

parse_eq <- function(input) {
    eq_key <- input$equation_key %||% NULL
    eq_gender <- input$equation_gender %||% NULL
    eq_info <- input$eq_info %||% NULL

    if (is.null(eq_key) && is.null(eq_gender) && !is.null(eq_info)) {
        parts <- strsplit(eq_info, "_", fixed = TRUE)[[1]]
        if (length(parts) >= 2) {
            eq_key <- parts[1]
            eq_gender <- parts[2]
        }
    }

    legacy <- input$dictionary %||% NULL
    if (is.null(eq_key) && is.null(eq_gender) && !is.null(legacy)) {
        parts <- strsplit(legacy, "_", fixed = TRUE)[[1]]
        if (length(parts) >= 2) {
            eq_key <- parts[1]
            eq_gender <- parts[2]
        }
    }

    list(
        equation_key = eq_key %||% "us2010",
        equation_gender = eq_gender %||% "average"
    )
}

as_epa <- function(x, name) {
    v <- as.numeric(unlist(x))
    if (length(v) != 3 || any(is.na(v))) stop(sprintf("Invalid %s: expected numeric length 3.", name))
    v
}

make_event_df <- function(actor, object) {
    dims <- c("E", "P", "A")
    behavior_dummy <- c(0, 0, 0)

    data.frame(
        event_id = rep(1L, 9),
        event = rep("event_1", 9),
        element = rep(c("actor", "behavior", "object"), each = 3),
        term = rep(c("actor", "behavior", "object"), each = 3),
        component = rep(c("identity", "behavior", "identity"), each = 3),
        dimension = rep(dims, times = 3),
        estimate = c(actor, behavior_dummy, object),
        stringsAsFactors = FALSE
    )
}

input <- tryCatch(fromJSON(file("stdin"), flatten = TRUE), error = function(e) NULL)
if (is.null(input)) {
    write(toJSON(list(error = "Invalid JSON input."), auto_unbox = TRUE), stdout())
    quit(status = 0)
}

result <- tryCatch(
    {
        actor <- as_epa(input$actor, "actor")
        object <- as_epa(input$object, "object")
        eq <- parse_eq(input)

        d <- make_event_df(actor, object)

        opt <- inteRact::optimal_behavior(
            d = d,
            equation_key = eq$equation_key,
            equation_gender = eq$equation_gender
        )

        # Return numeric length-3
        opt_vec <- as.numeric(unlist(opt))[1:3]

        list(
            optimal_behavior = opt_vec,
            meta = list(
                equation_key = eq$equation_key,
                equation_gender = eq$equation_gender
            )
        )
    },
    error = function(e) {
        list(error = e$message)
    }
)

write(toJSON(result, auto_unbox = TRUE), stdout())
