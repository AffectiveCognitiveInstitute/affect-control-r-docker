
import sys
import json
from act_api import init_conversation, step_conversation

def run_test():
    print("Initializing conversation: Doctor - Patient")
    try:
        # Note: 'doctor' and 'patient' are standard terms usually in US dictionaries
        state = init_conversation("Doctor", "Patient", dictionary="default")
        print("Initialization successful.")
        print(f"Actor: {state['actor']['term']} {state['actor']['epa']}")
        print(f"Object: {state['object']['term']} {state['object']['epa']}")
    except Exception as e:
        print(f"Initialization failed: {e}")
        return False

    print("\nExecuting step: Doctor checks Patient")
    try:
        # 'checks' or 'instructs' or 'advises'
        state = step_conversation(state, "checks")
        result = state["last_result"]
        
        print("Step successful.")
        print(f"Transients: {result['transients']}")
        print(f"Deflection: {result['deflection']}")
        
        # Validation
        if not all(k in result['transients'] for k in ['actor', 'behavior', 'object']):
            print("FAILED: Missing transient components")
            return False
            
        if not isinstance(result['deflection'], (int, float)):
             print("FAILED: Deflection is not numeric")
             return False
             
        return True
        
    except Exception as e:
        print(f"Step execution failed: {e}")
        # Print full traceback if needed, but error message is often enough for smoke test
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if run_test():
        print("\nSMOKE TEST PASSED")
        sys.exit(0)
    else:
        print("\nSMOKE TEST FAILED")
        sys.exit(1)
