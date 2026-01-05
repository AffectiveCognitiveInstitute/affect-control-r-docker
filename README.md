# Affect Control Theory (ACT) Runtime

This repository contains a Dockerized environment for Affect Control Theory research, bridging Python and R.

## Features
- **R Runtime**: Includes `inteRact`, `actdata`, and `bayesactR`.
- **Python API**: A minimal wrapper to perform EPA lookups, transient impression calculations, and deflection analysis using the R backend.

## Quick Start

You can pull and run the pre-built image directly from DockerHub:

```bash
docker run -p 5000:5000 createiflabs/affect-control-r-docker:latest
```

Or build it locally:
```bash
docker build -t act-r-runtime .
```

Run the container:
```bash
docker run -p 5000:5000 act-r-runtime
```

## Python API Usage
The `act_api.py` module provides the core functionality.

```python
from act_api import init_conversation, step_conversation

# Initialize a state with Actor and Object
state = init_conversation("Doctor", "Patient")

# Evaluate an event (Actor performs Behavior on Object)
state = step_conversation(state, "checks")

print(f"Deflection: {state['last_result']['deflection']}")
print(f"Transient Impressions: {state['last_result']['transients']}")
```

## Testing
Run the smoke test to verify the Python-R bridge:
```bash
python3 test_act_flow.py
```
*(Ensure you are running this inside the container or have R/Python dependencies locally)*
