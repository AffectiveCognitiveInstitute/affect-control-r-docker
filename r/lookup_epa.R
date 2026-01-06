suppressPackageStartupMessages({
  library(jsonlite)
  library(actdata)
})

input <- fromJSON(file("stdin"), flatten = TRUE)
label <- input$label
type <- input$type
dictionary_key <- input$dictionary %||% "usfullsurveyor2015" # besserer Default-Key

# robustes Laden über actdata-Key
dict_df <- actdata::epa_subset(dataset = dictionary_key)

if (!is.data.frame(dict_df) || nrow(dict_df) == 0) {
  write(toJSON(list(error = paste("Dictionary key not found or empty:", dictionary_key)),
    auto_unbox = TRUE
  ), stdout())
  quit(status = 0)
}

# komponentenbasiert filtern: identity / behavior / modifier / setting
# actdata nutzt oft 'component' (identity/behavior/modifier/setting)
component_map <- list(
  identity = "identity",
  behavior = "behavior",
  modifier = "modifier",
  setting  = "setting"
)

comp <- component_map[[tolower(type)]]
if (is.null(comp)) {
  write(toJSON(list(error = paste("Invalid type:", type)), auto_unbox = TRUE), stdout())
  quit(status = 0)
}

lbl_lower <- tolower(label)
match <- subset(dict_df, component == comp & tolower(term) == lbl_lower)

if (nrow(match) == 0) {
  write(toJSON(list(error = paste("Term not found:", label, "in", dictionary_key, "component", comp)),
    auto_unbox = TRUE
  ), stdout())
  quit(status = 0)
}

row <- match[1, ]
write(toJSON(list(
  term = row$term,
  epa = c(as.numeric(row$E), as.numeric(row$P), as.numeric(row$A)),
  metadata = as.list(row)
), auto_unbox = TRUE), stdout())
