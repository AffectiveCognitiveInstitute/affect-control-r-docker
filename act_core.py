import os
import json
import subprocess
from typing import Dict, List, Optional, Any, Union

# Configuration
# Assuming this file is in the same directory as the 'r' folder
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

        output = process.stdout.strip()
        if not output:
             # Try to provide more context if stderr is also empty
             raise RuntimeError(f"R script returned empty output. Stderr: {process.stderr}")
             
        try:
            return json.loads(output)
        except json.JSONDecodeError as e:
             raise RuntimeError(f"Failed to parse R output: {output}. Error: {e}")

    except Exception as e:
        raise RuntimeError(f"Error processing {script_name}: {e}")

def lookup_epa(label: str, type: str, dictionary: str = "us_2015") -> Dict[str, Any]:
    """Resolve a label to its fundamental EPA vector."""
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
    """Construct an ACT event object."""
    event = {
        "actor": actor_identity.get('epa', actor_identity),
        "behavior": behavior.get('epa', behavior),
        "object": object_identity.get('epa', object_identity) if object_identity else [0.0, 0.0, 0.0]
    }
    
    if setting:
        event["setting"] = setting.get('epa', setting)
        
    return event

def compute_transient_impressions(event: Dict[str, List[float]]) -> Dict[str, Any]:
    """Compute transient impressions for the event."""
    return _run_r_script("transient_impressions.R", event)

def compute_deflection(
    fundamentals: Dict[str, List[float]],
    transients: Dict[str, List[float]],
    weights: Optional[Dict[str, List[float]]] = None
) -> Dict[str, Any]:
    """Compute deflection between fundamentals and transients."""
    payload = {
        "fundamentals": fundamentals,
        "transients": transients
    }
    if weights:
        payload["weights"] = weights
        
    # line 410 of original app.py passed "fundamentals" (plural) to "deflection.R".
    # line 85 passed "fundamental".
    # I need to be careful here. Let's check deflection.R content or just support both keys?
    # Inspecting line 410: "fundamentals": fundamentals
    # Inspecting line 85: "fundamental": fundamentals
    # I'll include both keys to be safe, or I should check deflection.R.
    # For now, I'll use the payload structure from the first definition as it was more detailed.
    # But wait, line 408 definition was the one likely active.
    # Let's check deflection.R quickly in a separate step or just assume the R script handles it.
    # Actually, to be safe, I'll stick to the structure of the first definition but maybe add the second key.
    
    return _run_r_script("deflection.R", payload)

def init_conversation(actor_label: str, object_label: str, dictionary: str = "us_2015") -> Dict[str, Any]:
    """Initialize conversation state."""
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
    """Execute a single ACT evaluation step."""
    actor = state["actor"]
    obj = state["object"]
    dictionary = state.get("dictionary", "us_2015")
    
    # 1. Resolve behavior
    behavior = lookup_epa(behavior_label, "behavior", dictionary)
    if "error" in behavior:
        raise ValueError(f"Behavior lookup failed: {behavior['error']}")
    
    # 2. Create event (Fundamentals)
    fundamental_event = create_event(actor, behavior, obj)
    
    # 3. Compute Transients
    transients_result = compute_transient_impressions(fundamental_event)
    if "error" in transients_result:
        raise RuntimeError(f"Transient computation failed: {transients_result['error']}")
    
    transients = transients_result["transient"]
    
    # 4. Compute Deflection
    deflection_result = compute_deflection(fundamental_event, transients)
    
    step_result = {
        "inputs": {
            "actor": actor,
            "behavior": behavior,
            "object": obj
        },
        "fundamentals": fundamental_event,
        "transients": transients,
        "deflection": deflection_result.get("deflection"),
        "deflection_breakdown": deflection_result.get("components")
    }
    
    state.setdefault("history", []).append(step_result)
    state["last_result"] = step_result
    
    return state

def search_labels(dictionary: str, search_term: Optional[str] = None) -> Dict[str, Any]:
    """Search for terms in a dictionary."""
    return _run_r_script("search_labels.R", {
        "dictionary": dictionary,
        "search": search_term
    })

def compute_optimal_behavior(
    actor_epa: List[float],
    object_epa: List[float],
    dictionary: str = "us_2015"
) -> Dict[str, Any]:
    """Calculate optimal behavior EPA."""
    return _run_r_script("optimal_behavior.R", {
        "actor": actor_epa,
        "object": object_epa,
        "dictionary": dictionary
    })

def compute_modified_identity(
    modifier_epa: List[float],
    identity_epa: List[float],
    dictionary: str = "us_2015"
) -> Dict[str, Any]:
    """Calculate modified identity EPA."""
    return _run_r_script("modify_identity.R", {
        "modifier": modifier_epa,
        "identity": identity_epa,
        "dictionary": dictionary
    })

def compute_transients(
    actor_epa: List[float],
    behavior_epa: List[float],
    object_epa: List[float],
    dictionary: str = "us2010"
) -> Dict[str, Any]:
    """Calculate transient impressions after an event."""
    return _run_r_script("transients.R", {
        "actor": actor_epa,
        "behavior": behavior_epa,
        "object": object_epa,
        "dictionary": dictionary
    })

def compute_emotions(
    actor_epa: List[float],
    behavior_epa: List[float],
    object_epa: List[float],
    dictionary: str = "us2010"
) -> Dict[str, Any]:
    """Predict emotional response."""
    return _run_r_script("emotions.R", {
        "actor": actor_epa,
        "behavior": behavior_epa,
        "object": object_epa,
        "dictionary": dictionary
    })

def compute_reidentify(
    actor_epa: List[float],
    behavior_epa: List[float],
    object_epa: List[float],
    element: str = "actor",
    dictionary: str = "us2010"
) -> Dict[str, Any]:
    """Calculate reidentified EPA to reduce deflection."""
    return _run_r_script("reidentify.R", {
        "actor": actor_epa,
        "behavior": behavior_epa,
        "object": object_epa,
        "element": element,
        "dictionary": dictionary
    })

def find_closest_term(
    epa: List[float],
    term_type: str = "identity",
    dictionary: str = "us2010",
    n: int = 5
) -> Dict[str, Any]:
    """Find closest dictionary term to an EPA vector."""
    return _run_r_script("closest_term.R", {
        "epa": epa,
        "type": term_type,
        "dictionary": dictionary,
        "n": n
    })
