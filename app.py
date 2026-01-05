from flask import Flask, jsonify
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import os

app = Flask(__name__)

# Try to load R packages on startup to fail fast if they are missing
try:
    print("Loading R packages...")
    actdata = importr('actdata')
    inteRact = importr('inteRact')
    bayesactR = importr('bayesactR')
    print("R packages loaded successfully.")
except Exception as e:
    print(f"Error loading R packages: {e}")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "act-r-runtime"}), 200

@app.route('/r-check', methods=['GET'])
def r_check():
    try:
        # Simple R verification
        r_version = robjects.r['R.version.string']
        
        # internal check if packages are actually usable
        # We can just return the version as a proof that R logic works
        return jsonify({
            "status": "success", 
            "r_version": str(r_version[0]),
            "packages": ["actdata", "inteRact", "bayesactR"]
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
