# Affect Control Theory (ACT) Runtime

This repository contains a Dockerized environment for Affect Control Theory research, bridging Python and R.

## Features
- **R Runtime**: Includes `inteRact`, `actdata`, and `bayesactR`.
- **Python API**: A minimal wrapper to perform EPA lookups, transient impression calculations, and deflection analysis using the R backend.

## Quick Start

You can pull and run the pre-built image directly from DockerHub:

```bash
docker run -p 5000:5000 createiflabs/affect-control-r-docker:main
```

Or build it locally:
```bash
docker build -t act-r-runtime .
```

Run the container in **REST API mode** (default):
```bash
docker run -p 5000:5000 act-r-runtime
```

Run the container in **MCP Server mode**:
```bash
docker run -i act-r-runtime --env RUN_MODE=MCP
```
*Note: MCP mode uses stdio, so remove `-p` and use `-i` (interactive) or pipe input depending on your client.*


## API Reference

The application exposes the following REST endpoints:

### GET /health
Returns the service health status.
- **Response**: `{"status": "healthy", ...}`

### GET /r-check
Verifies the R environment, installed packages (`actdata`, `inteRact`, `bayesactR`), and available dictionaries.
- **Response**: `{"status": "success/warning", "packages": {...}, "dictionaries": [...]}`

### GET /act/dictionaries
Returns a list of all available ACT dictionaries in the installed `actdata` package.
- **Response**: `{"dictionaries": ["us_2015", "germany2007", ...]}`

### GET /act/labels
Search for terms in a specific dictionary.
- **Input Params**: `dictionary` (required), `search` (optional regex)
- **Response**: `{"dictionary": "us_2015", "count": 1, "terms": ["doctor"]}`

### POST /act/lookup
Resolve a term to its EPA values.
- **Input**: `{"label": "doctor", "type": "identity", "dictionary": "us_2015"}`
- **Response**: `{"term": "doctor", "epa": [2.3, 1.5, 0.8], ...}`

### POST /act/optimize
Calculate the optimal behavior for a given Actor toward an Object in a specific context.
- **Input**: `{"actor": [2.3, 1.5,  0.8], "object": [-1.0, 2.0, 0.5], "dictionary": "us_2015"}`
- **Response**: `{"optimal_behavior": [1.2, 0.5, 0.1]}`

### POST /act/modify
Calculate the EPA of a modified identity (Amalgamation).
- **Input**: `{"modifier": [1.0, 1.0, 1.0], "identity": [2.0, 2.0, 2.0], "dictionary": "us_2015"}`
- **Response**: `{"modified_identity": [1.5, 1.5, 1.5]}`

### POST /act/init
Initialize a conversation state.
- **Input**: `{"actor": "doctor", "object": "patient", "dictionary": "us_2015"}`
- **Response**: `{"actor": {...}, "object": {...}, "history": []}`

### POST /act/step
Step through an event in the simulation.
- **Input**:
  ```json
  {
    "state": { ... },
    "behavior": "advises"
  }
  ```
- **Response**: Updated state with event deflection and transient impressions.

### POST /act/deflection
Calculate deflection between fundamental and transient impressions.
- **Input**: `{"fundamentals": [1.0, 1.0, 1.0], "transients": [2.0, 2.0, 2.0]}`
- **Response**: `{"deflection": 3.0}`

### POST /act/transients
Calculate transient impressions after an event.
- **Input**: `{"actor": [...], "behavior": [...], "object": [...], "dictionary": "us_2015"}`
- **Response**: `{"actor_transient": [...], "behavior_transient": [...], "object_transient": [...]}`

### POST /act/emotions
Predict characterizing emotions for the interactants.
- **Input**: `{"actor": [...], "behavior": [...], "object": [...], "dictionary": "us_2015"}`
- **Response**: `{"actor_emotion": {"epa": [...], "label": "happy"}, "object_emotion": ...}`

### POST /act/reidentify
Calculate reidentified EPA to reduce deflection for a specific element (actor, behavior, or object).
- **Input**: `{"actor": [...], "behavior": [...], "object": [...], "element": "actor", "dictionary": "us_2015"}`
- **Response**: `{"reidentified_epa": [...]}`

### POST /act/closest
Find the closest dictionary term to a given EPA vector.
- **Input**: `{"epa": [2.5, 1.5, 0.5], "type": "identity", "dictionary": "us_2015", "n": 3}`
- **Response**: `{"matches": [{"term": "doctor", "distance": 0.1, "epa": [...]}, ...]}`

## Analysis Workflow

Here is how to perform a complete ACT analysis using the API:

1.  **Select a Dictionary**:
    -   `GET /act/dictionaries` -> Identify `"us_2015"`.

2.  **Find Terms**:
    -   `GET /act/labels?dictionary=us_2015&search=doctor` -> Confirm "doctor" exists.
    -   `GET /act/labels?dictionary=us_2015&search=patient` -> Confirm "patient" exists.

3.  **Initialize or Lookup**:
    -   `POST /act/init` with `actor="doctor"` and `object="patient"`.
    -   *Or* lookup individual EPAs via `POST /act/lookup`.

4.  **Determine Optimal Action**:
    -   Use the EPAs from step 3.
    -   `POST /act/optimize` with `{"actor": [...], "object": [...]}`.
    -   Result: EPA of the theoretically optimal behavior.

5.  **Simulate Event**:
    -   Choose a behavior (either the optimal one or a specific label like "advises").
    -   `POST /act/step` to get the resulting deflection and transient sentiments.

## Model Context Protocol (MCP) Interface

This package exposes ACT capabilities as MCP tools, allowing AI agents to directly perform calculations and simulations.

### Prerequisites for MCP
The MCP Python SDK requires **Python 3.10 or higher**. If your main environment uses an older version (e.g., 3.9), you must create a separate virtual environment for the MCP server.

### Setup
1. Create a Python 3.10+ virtual environment:
   ```bash
   # Windows (example)
   py -3.10 -m venv venv_mcp
   
   # Linux/macOS
   python3.10 -m venv venv_mcp
   ```
2. Activate and install dependencies:
   ```bash
   # Windows
   .\venv_mcp\Scripts\activate
   pip install -r requirements-mcp.txt
   
   # Linux/macOS
   source venv_mcp/bin/activate
   pip install -r requirements-mcp.txt
   ```

### Running the MCP Server
Start the server using stdio transport (standard input/output):
```bash
python mcp_server.py
```
Models or IDEs supporting MCP can now spawn this process to access ACT tools.

### Available Tools
The server dynamically exposes public functions from the `act_core` module. Current capabilities include:
- **Lookup**: `lookup_epa`, `search_labels`
- **Simulation**: `init_conversation`, `step_conversation`
- **Computation**: `compute_transients`, `compute_deflection`, `compute_optimal_behavior`, `compute_modified_identity`, `compute_reidentify`, `compute_emotions`
- **Utility**: `create_event`, `find_closest_term`

### Extending the Interface
To add a new tool:
1.  Define a new public function in `act_core.py`.
2.  Add type hints and a docstring (these are used to generate the tool schema).
3.  Restart the MCP server. The function will be automatically discovered and registered.

## Python API Usage (Internal)
The `app.py` module contains the core logic moved from the deprecated `act_api.py`. It is primarily designed to be consumed via the HTTP endpoints above, but relies on `act_core.py` for all business logic.


## Local Development

To set up a local virtual environment for development and testing:

### Prerequisites

1. **Install R**: Ensure R is installed on your system.
   - **Windows**: Download and install from [CRAN](https://cran.r-project.org/bin/windows/base/).
   - **macOS**: Download and install from [CRAN](https://cran.r-project.org/bin/macosx/).
   - **Linux**: `sudo apt-get install r-base`

2. **Set R_HOME**: `rpy2` requires the `R_HOME` environment variable.
   - **Windows**:
     ```powershell
     # PowerShell example (adjust version)
     $env:R_HOME = "C:\Program Files\R\R-4.5.2"
     ```
   - **Linux/macOS**:
     ```bash
     export R_HOME=$(R RHOME)
     ```

### Setup Venv


```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\activate

# Activate virtual environment (Linux/macOS)
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run
python ./app.py
```

## Testing
Run the smoke test to verify the Python-R bridge:
```bash
python3 test_act_flow.py
```
*(Ensure you are running this inside the container or have R/Python dependencies locally)*
