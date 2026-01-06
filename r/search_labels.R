suppressPackageStartupMessages({
    library(jsonlite)
    library(actdata)
})

input <- tryCatch(fromJSON(file("stdin"), flatten = TRUE), error = function(e) list(dictionary = NULL))
dictionary_key <- input$dictionary
search_term <- input$search

if (is.null(dictionary_key) || dictionary_key == "") {
    write(toJSON(list(error = "Dictionary parameter is required"), auto_unbox = TRUE), stdout())
    quit(status = 0)
}

df <- actdata::epa_subset(dataset = dictionary_key)
if (!is.data.frame(df) || nrow(df) == 0 || is.null(df$term)) {
    write(toJSON(list(error = paste("Dictionary key not found or empty:", dictionary_key)), auto_unbox = TRUE), stdout())
    quit(status = 0)
}

terms <- df$term
if (!is.null(search_term) && search_term != "") {
    matches <- grep(search_term, terms, ignore.case = TRUE, value = TRUE)
} else {
    matches <- terms
}

if (length(matches) > 100) matches <- head(matches, 100)

write(toJSON(list(dictionary = dictionary_key, count = length(matches), terms = matches),
    auto_unbox = TRUE
), stdout())
