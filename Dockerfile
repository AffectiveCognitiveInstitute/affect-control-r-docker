# Fixed, newer R version that is known to work
FROM rocker/r-ver:4.5.2

# Environment
ENV DEBIAN_FRONTEND=noninteractive
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# System dependencies
# Includes everything needed for:
# - rpy2 linking
# - compiling common R packages
# - GitHub installs via remotes
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    git \
    libcurl4-openssl-dev \
    libxml2-dev \
    libssl-dev \
    libgit2-dev \
    libpcre2-dev \
    libdeflate-dev \
    liblzma-dev \
    libbz2-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Python environment
WORKDIR /app
COPY requirements.txt .

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --no-cache-dir -r requirements.txt

# R packages (ACT + BayesACT)
COPY install_packages.R .
RUN Rscript install_packages.R

# Application code
COPY app.py .

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
