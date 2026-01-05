# install_packages.R
# Minimal, deterministic runtime install for ACT / BayesACT

options(repos = c(CRAN = "https://cloud.r-project.org"))

install_cran_or_stop <- function(pkgs) {
    message("Installing CRAN packages: ", paste(pkgs, collapse = ", "))
    install.packages(pkgs, quiet = TRUE)
    missing <- pkgs[!vapply(pkgs, requireNamespace, logical(1), quietly = TRUE)]
    if (length(missing) > 0) {
        stop("Failed to install CRAN packages: ", paste(missing, collapse = ", "))
    }
}

install_github_or_stop <- function(repo, ref = NULL) {
    if (!requireNamespace("remotes", quietly = TRUE)) {
        stop("remotes is required but not installed")
    }
    spec <- if (is.null(ref)) repo else paste0(repo, "@", ref)
    message("Installing GitHub package: ", spec)
    remotes::install_github(
        spec,
        upgrade = "never",
        dependencies = TRUE,
        quiet = TRUE
    )
}

# Lightweight CRAN essentials for runtime + JSON I/O
install_cran_or_stop(c("remotes", "jsonlite", "Rcpp"))

# Core ACT / BayesACT packages (authoritative GitHub sources)
install.packages("devtools")
devtools::install_github("ahcombs/actdata")
devtools::install_github("ahcombs/bayesactR")

# Optional: only include if your runtime explicitly depends on it
# install_github_or_stop("ekmaloney/inteRact")

# Fail fast if core packages do not load
message("Verifying ACT/BayesACT packages...")
library(actdata)
library(bayesactR)

message("ACT/BayesACT installation complete.")
