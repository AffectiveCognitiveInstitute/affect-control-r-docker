# Use rocker/r-ver as base to ensure fixed R version (4.4.0)
FROM rocker/r-ver:4.4.0

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install system dependencies
# We need python3, pip, and libraries for R packages (curl, xml2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    libcurl4-openssl-dev \
    libxml2-dev \
    libssl-dev \
    libgit2-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Setup Python environment
WORKDIR /app
COPY requirements.txt .

# Create virtual environment and install dependencies
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --no-cache-dir -r requirements.txt

# Install R packages
COPY install_packages.R .
RUN Rscript install_packages.R

# Copy application code
COPY app.py .

# Use non-root user (good practice, though sometimes tricky with R libs if defined globally)
# Rocker images usually have 'docker' or 'rstudio' user, but let's stick to root for simplicity 
# unless strictly required, or Create a new user. 
# For now, running as root is easiest for container operations unless specs demand otherwise.

# Expose port
EXPOSE 5000

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
