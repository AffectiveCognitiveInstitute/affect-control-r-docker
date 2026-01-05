import json
import subprocess
import os
from typing import Dict, List, Optional, Any, Union

# Configuration
R_SCRIPT_DIR = os.path.join(os.path.dirname(__file__), 'r')

def _run_r_script(script_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes an R script using subprocess, passing input as JSON via stdin
    and parsing output JSON from stdout.
    """
    script_path = os.path.join(R_SCRIPT_DIR, script_name)
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"R script not found: {script_path}")

    try:
        process = subprocess.run(
            ["Rscript", script_path],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            check=False
        )
        
        if process.returncode != 0:
            raise RuntimeError(f"R script failed with error:\n{process.stderr}")

        # R might output trailing newlines or other noise if not careful, 
        # but our scripts write exactly one JSON line or block.
        # However, Rscript might print loading messages if suppressPackageStartupMessages is not perfectly effective 
        # or if warnings occur.
        # We will try to parse the last valid JSON object or just the stdout.
        
        output = process.stdout.strip()
        if not output:
             raise RuntimeError(f"R script returned empty output. Stderr: {process.stderr}")
             
        try:
            return json.loads(output)
        except json.JSONDecodeError as e:
             raise RuntimeError(f"Failed to parse R output: {output}. Error: {e}")

    except Exception as e:
        raise RuntimeError(f"Error processing {script_name}: {e}")

def lookup_epa(label: str, type: str, dictionary: str = "us_2015") -> Dict[str, Any]:
    """
    Resolve a label to its fundamental EPA vector.
    
    Args:
        label: The word/term to look up (e.g., "doctor")
        type: "identity", "behavior", "modifier", or "setting"
        dictionary: The ACT dictionary to use
        
    Returns:
        Dict containing 'epa', 'term', and 'metadata'.
    """
    return _run_r_script("lookup_epa.R", {
        "label": label,
        "type": type,
        "dictionary": dictionary
    })

def create_event(
    actor_identity: Dict[str, Any],
    behavior: Dict[str, Any],
    object_identity: Optional[Dict[str, Any]] = None,
    setting: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Construct an ACT event object. In this format, an event is just a dictionary
    of the fundamental components.
    
    The inputs should be result objects from lookup_epa.
    """
    event = {
        "actor": actor_identity['epa'],
        "behavior": behavior['epa'],
        "object": object_identity['epa'] if object_identity else [0.0, 0.0, 0.0]
    }
    
    if setting:
        event["setting"] = setting['epa']
        
    return event

def compute_transient_impressions(
    event: Dict[str, List[float]],
    model: str = "default"
) -> Dict[str, Any]:
    """
    Compute transient impressions for the event.
    """
    return _run_r_script("transient_impressions.R", event)

def compute_deflection(
    fundamentals: Dict[str, List[float]],
    transients: Dict[str, List[float]],
    weights: Optional[Dict[str, List[float]]] = None
) -> Dict[str, Any]:
    """
    Compute deflection between fundamentals and transients.
    """
    payload = {
        "fundamental": fundamentals,
        "transient": transients
    }
    if weights:
        payload["weights"] = weights
        
    return _run_r_script("deflection.R", payload)

def init_conversation(
    actor_label: str,
    object_label: str,
    dictionary: str = "us_2015"
) -> Dict[str, Any]:
    """
    Initialize conversation state.
    """
    # Lookup identities
    actor = lookup_epa(actor_label, "identity", dictionary)
    obj = lookup_epa(object_label, "identity", dictionary)
    
    if "error" in actor:
        raise ValueError(f"Actor lookup failed: {actor['error']}")
    if "error" in obj:
        raise ValueError(f"Object lookup failed: {obj['error']}")
        
    return {
        "actor": actor,
        "object": obj,
        "history": [],
        "dictionary": dictionary
    }

def step_conversation(state: Dict[str, Any], behavior_label: str) -> Dict[str, Any]:
    """
    Execute a single ACT evaluation step.
    
    Args:
        state: Current conversation state (from init_conversation or previous step)
        behavior_label: The behavior being performed by the actor
        
    Returns:
        Updated state with 'last_result' containing calculation details.
    """
    actor = state["actor"]
    obj = state["object"]
    dictionary = state.get("dictionary", "us_2015")
    
    # 1. Resolve behavior
    behavior = lookup_epa(behavior_label, "behavior", dictionary)
    if "error" in behavior:
        raise ValueError(f"Behavior lookup failed: {behavior['error']}")
    
    # 2. Create event (Fundamentals)
    # Note: In a full simulation, 'Fundamentals' for the *next* step might be the *Transients* of the previous step
    # if we are doing identity update (learning). 
    # But for standard ACT event processing, we often use the fundamental identities 
    # OR the 'current conceptualization' of the identities.
    # For this simplified API, we use the stored identities.
    
    fundamental_event = create_event(actor, behavior, obj)
    
    # 3. Compute Transients
    transients_result = compute_transient_impressions(fundamental_event)
    if "error" in transients_result:
        raise RuntimeError(f"Transient computation failed: {transients_result['error']}")
    
    transients = transients_result["transient"]
    
    # 4. Compute Deflection
    deflection_result = compute_deflection(fundamental_event, transients)
    
    # 5. Pack result
    step_result = {
        "inputs": {
            "actor": actor,
            "behavior": behavior,
            "object": obj
        },
        "fundamentals": fundamental_event,
        "transients": transients,
        "deflection": deflection_result["deflection"],
        "deflection_breakdown": deflection_result.get("components")
    }
    
    # Append to history
    state["history"].append(step_result)
    state["last_result"] = step_result
    
    return state
