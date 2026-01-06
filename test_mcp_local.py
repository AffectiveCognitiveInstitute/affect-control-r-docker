import subprocess
import json
import sys
import os

def run_test():
    # Path to python interpreter in venv_mcp
    python_exe = os.path.join(os.getcwd(), "venv_mcp", "Scripts", "python.exe")
    server_script = "mcp_server.py"
    
    # Start the server process
    process = subprocess.Popen(
        [python_exe, server_script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,
        text=True,
        bufsize=0  # Unbuffered communication
    )
    
    print(f"Started MCP server with PID {process.pid}")

    def send_request(method, params=None, msg_id=None):
        req = {
            "jsonrpc": "2.0",
            "method": method
        }
        if params is not None:
            req["params"] = params
        if msg_id is not None:
            req["id"] = msg_id
            
        json_str = json.dumps(req)
        # print(f"\n--- Request ({method}) ---") 
        process.stdin.write(json_str + "\n")
        process.stdin.flush()

    def read_response():
        line = process.stdout.readline()
        if not line:
            return None
        return json.loads(line)

    def parse_tool_result(resp):
        if not resp or "result" not in resp:
            print("Error: Invalid response format")
            return None
        
        content = resp["result"].get("content", [])
        if not content:
            print("Error: No content in result")
            return None
            
        text_content = content[0].get("text", "")
        # print(f"\nResponse Text: {text_content[:100]}...") 
        
        try:
            return json.loads(text_content)
        except json.JSONDecodeError:
            print("Error: Failed to parse inner JSON content")
            return None

    try:
        # 1. Initialize
        send_request("initialize", {
            "protocolVersion": "2024-11-05", 
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"}
        }, 1)
        read_response() 
        send_request("notifications/initialized")
        
        # 2. Search for behavior (to emulate user flow)
        print("\n\n=== TEST 1: Search Labels (behavior) ===")
        # Searching for something common
        send_request("tools/call", {
            "name": "search_labels",
            "arguments": {
                "dictionary": "uga2015",
                "search_term": "advise" 
            }
        }, 2)
        resp = read_response()
        data = parse_tool_result(resp)
        behavior_term = "advise" # fallback
        if data and data.get("ok"):
             print("SUCCESS: Search Labels")
             # Try to pick a term that looks like a behavior if possible, 
             # or just use the first one if search_labels returns a list of strings
             # The R script output structure: { "result": { "matches": [...] } } or similar?
             # Let's inspect data['data']
             matches = data['data']
             if matches and isinstance(matches, list) and len(matches) > 0:
                 behavior_term = matches[0]
                 print(f"Found term: {behavior_term}")
        else:
             print("FAILED: Search Labels")

        # 3. Lookup EPA
        print(f"\n\n=== TEST 2: Lookup EPA ({behavior_term}) ===")
        send_request("tools/call", {
            "name": "lookup_epa",
            "arguments": {
                "label": behavior_term,
                "type": "behavior",
                "dictionary": "uga2015"
            }
        }, 3)
        
        resp = read_response()
        data = parse_tool_result(resp)
        if data and data.get("ok"):
             print("SUCCESS: Lookup EPA")
        else:
             print(f"FAILED: Lookup EPA for {behavior_term}")

        # 4. Init Conversation
        print("\n\n=== TEST 3: Init Conversation ===")
        send_request("tools/call", {
            "name": "init_conversation",
            "arguments": {
                "actor_label": "doctor",
                "object_label": "patient",
                "dictionary": "uga2015"
            }
        }, 4)
        
        resp = read_response()
        data = parse_tool_result(resp)
        state = None
        if data and data.get("ok"):
             print("SUCCESS: Init Conversation")
             state = data["data"]
        else:
             print("FAILED: Init Conversation")
             
        # 5. Compute Optimal Behavior
        if state:
            print("\n\n=== TEST 4: Compute Optimal Configuration ===")
            actor_epa = state["actor"]["epa"]
            object_epa = state["object"]["epa"]
            
            send_request("tools/call", {
                "name": "compute_optimal_behavior",
                "arguments": {
                    "actor_epa": actor_epa,
                    "object_epa": object_epa,
                    "dictionary": "uga2015"
                }
            }, 5)
            resp = read_response()
            data = parse_tool_result(resp)
            if data and data.get("ok"):
                 print("SUCCESS: Optimal Behavior")
            else:
                 print("FAILED: Optimal Behavior")

        # 6. Step Conversation
        if state:
            print(f"\n\n=== TEST 5: Step Conversation (behavior: {behavior_term}) ===")
            send_request("tools/call", {
                "name": "step_conversation",
                "arguments": {
                    "state": state,
                    "behavior_label": behavior_term 
                }
            }, 6)
            
            resp = read_response()
            data = parse_tool_result(resp)
            if data and data.get("ok"):
                 print("SUCCESS: Step Conversation")
                 # print(json.dumps(data["data"], indent=2)[:500])
            else:
                 print("FAILED: Step Conversation")
                 if data and "error" in data:
                     print(f"Error: {data['error']}")
        
    finally:
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    run_test()
