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

make_modifier_df <- function(modifier, identity) {
    dims <- c("E", "P", "A")
    data.frame(
        event_id = rep(1L, 6),
        event = rep("event_1", 6),
        element = rep(c("actor_modifier", "actor"), each = 3),
        term = rep(c("modifier", "identity"), each = 3),
        component = rep(c("modifier", "identity"), each = 3),
        dimension = rep(dims, times = 2),
        estimate = c(modifier, identity),
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
        modifier <- as_epa(input$modifier, "modifier")
        identity <- as_epa(input$identity, "identity")
        eq <- parse_eq(input)

        d <- make_modifier_df(modifier, identity)

        out <- inteRact::modify_identity(
            d = d,
            equation_key = eq$equation_key,
            equation_gender = eq$equation_gender
        )

        out_vec <- as.numeric(unlist(out))[1:3]

        list(
            modified_identity = out_vec,
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
