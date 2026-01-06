import urllib.request
import json
import sys

BASE_URL = "http://localhost:5000"

def make_request(url, method="GET", data=None):
    try:
        req = urllib.request.Request(url, method=method)
        req.add_header('Content-Type', 'application/json')
        
        if data:
            json_data = json.dumps(data).encode('utf-8')
            req.data = json_data
            
        with urllib.request.urlopen(req) as f:
            resp_body = f.read().decode('utf-8')
            return f.status, resp_body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return 0, str(e)

def test_labels():
    print("Testing /act/labels...")
    # Manual query param construction - use 'adult' which exists in germany2007
    url = f"{BASE_URL}/act/labels?dictionary=germany2007&search=adult"
    status, body = make_request(url)
    print(f"Status: {status}")
    print(f"Response: {body}")
    
    if status == 200:
        try:
            data = json.loads(body)
            if "terms" in data and len(data["terms"]) > 0:
                print("PASS")
                return
        except: pass
    print("FAIL")

def test_lookup():
    print("\nTesting /act/lookup...")
    url = f"{BASE_URL}/act/lookup"
    payload = {
        "label": "adult",
        "type": "identity",
        "dictionary": "germany2007"
    }
    status, body = make_request(url, method="POST", data=payload)
    print(f"Status: {status}")
    print(f"Response: {body}")
    
    if status == 200:
        try:
            data = json.loads(body)
            if "epa" in data and len(data["epa"]) == 3:
                 print("PASS")
                 return
        except: pass
    print("FAIL")

def test_optimize():
    print("\nTesting /act/optimize...")
    url = f"{BASE_URL}/act/optimize"
    payload = {
        "actor": [2.3, 1.5, 0.8],
        "object": [-1.0, 2.0, 0.5],
        "dictionary": "germany2007"
    }
    status, body = make_request(url, method="POST", data=payload)
    print(f"Status: {status}")
    print(f"Response: {body}")
    
    if status == 200:
        try:
            data = json.loads(body)
            if "optimal_behavior" in data:
                 print("PASS")
                 return
        except: pass
    print("FAIL")

def test_modify():
    print("\nTesting /act/modify...")
    url = f"{BASE_URL}/act/modify"
    payload = {
        "modifier": [1.0, 1.0, 1.0],
        "identity": [2.0, 2.0, 2.0],
        "dictionary": "germany2007"
    }
    status, body = make_request(url, method="POST", data=payload)
    print(f"Status: {status}")
    print(f"Response: {body}")
    
    if status == 200:
        try:
            data = json.loads(body)
            if "modified_identity" in data:
                 print("PASS")
                 return
        except: pass
    print("FAIL")


def test_deflection():
    print("\nTesting /act/deflection...")
    url = f"{BASE_URL}/act/deflection"
    payload = {
        "fundamentals": {
            "actor": [2.0, 1.5, 0.5],
            "behavior": [1.0, 1.0, 1.0],
            "object": [0.5, 0.5, 0.5]
        },
        "transients": {
            "actor": [1.8, 1.3, 0.4],
            "behavior": [0.8, 0.9, 0.9],
            "object": [0.4, 0.4, 0.4]
        }
    }
    status, body = make_request(url, method="POST", data=payload)
    print(f"Status: {status}")
    print(f"Response: {body}")
    
    if status == 200:
        try:
            data = json.loads(body)
            if "deflection" in data and "total" in data["deflection"]:
                 print("PASS")
                 return
        except: pass
    print("FAIL")


def test_transients():
    print("\nTesting /act/transients...")
    url = f"{BASE_URL}/act/transients"
    payload = {
        "actor": [2.0, 1.5, 0.5],
        "behavior": [1.0, 1.0, 1.0],
        "object": [0.5, 0.5, 0.5],
        "dictionary": "us2010"
    }
    status, body = make_request(url, method="POST", data=payload)
    print(f"Status: {status}")
    print(f"Response: {body}")
    
    if status == 200:
        try:
            data = json.loads(body)
            if "transients" in data:
                 print("PASS")
                 return
        except: pass
    print("FAIL")


def test_emotions():
    print("\nTesting /act/emotions...")
    url = f"{BASE_URL}/act/emotions"
    payload = {
        "actor": [2.0, 1.5, 0.5],
        "behavior": [1.0, 1.0, 1.0],
        "object": [0.5, 0.5, 0.5],
        "dictionary": "us2010"
    }
    status, body = make_request(url, method="POST", data=payload)
    print(f"Status: {status}")
    print(f"Response: {body}")
    
    if status == 200:
        try:
            data = json.loads(body)
            if "emotions" in data:
                 print("PASS")
                 return
        except: pass
    print("FAIL")


def test_reidentify():
    print("\nTesting /act/reidentify...")
    url = f"{BASE_URL}/act/reidentify"
    payload = {
        "actor": [2.0, 1.5, 0.5],
        "behavior": [1.0, 1.0, 1.0],
        "object": [0.5, 0.5, 0.5],
        "element": "actor",
        "dictionary": "us2010"
    }
    status, body = make_request(url, method="POST", data=payload)
    print(f"Status: {status}")
    print(f"Response: {body}")
    
    if status == 200:
        try:
            data = json.loads(body)
            if "reidentified" in data:
                 print("PASS")
                 return
        except: pass
    print("FAIL")


def test_closest():
    print("\nTesting /act/closest...")
    url = f"{BASE_URL}/act/closest"
    payload = {
        "epa": [2.0, 1.5, 0.5],
        "type": "identity",
        "dictionary": "germany2007",
        "n": 3
    }
    status, body = make_request(url, method="POST", data=payload)
    print(f"Status: {status}")
    print(f"Response: {body}")
    
    if status == 200:
        try:
            data = json.loads(body)
            if "matches" in data and len(data["matches"]) > 0:
                 print("PASS")
                 return
        except: pass
    print("FAIL")


if __name__ == "__main__":
    test_lookup()
    test_labels()
    test_optimize()
    test_modify()
    test_deflection()
    test_transients()
    test_emotions()
    test_reidentify()
    test_closest()

