import requests
import time
import sys

def test_health():
    url = "http://localhost:5000/health"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Health check passed: " + response.text)
            return True
        else:
            print(f"Health check failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"Health check failed with exception: {e}")
        return False

def test_r_check():
    url = "http://localhost:5000/r-check"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success" and "inteRact" in data.get("packages", []):
                print("R check passed: " + response.text)
                return True
            else:
                print("R check returned success but unexpected content: " + response.text)
                return False
        else:
            print(f"R check failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"R check failed with exception: {e}")
        return False

if __name__ == "__main__":
    print("Waiting for service to be up...")
    # Retrying a few times in case container is still starting
    for i in range(10):
        if test_health():
            break
        time.sleep(2)
        print(f"Retry {i+1}...")
    
    if not test_health():
        print("Service not reachable. Exiting.")
        sys.exit(1)

    if not test_r_check():
        print("R functionality check failed.")
        sys.exit(1)
        
    print("All smoke tests passed!")
    sys.exit(0)
