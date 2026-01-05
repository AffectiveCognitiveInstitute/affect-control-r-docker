FROM rocker/r-ver:4.5.2

ENV DEBIAN_FRONTEND=noninteractive
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Required for rpy2 to find R shared libraries
ENV R_HOME=/usr/local/lib/R
ENV LD_LIBRARY_PATH=/usr/local/lib/R/lib:$LD_LIBRARY_PATH

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
    libzstd-dev \
    # Required for R packages: systemfonts, textshaping, ragg (devtools deps)
    libfontconfig1-dev \
    libfreetype6-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libpng-dev \
    libtiff5-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --no-cache-dir -r requirements.txt

COPY install_packages.R .
RUN Rscript install_packages.R

COPY app.py .


ENV PYTHONUNBUFFERED=1

# Create a non-root user
RUN useradd -m -u 1000 appuser

# Change ownership of application and virtual environment
RUN chown -R appuser:appuser /app /opt/venv

USER 1000

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "--log-level", "debug", "app:app"]
