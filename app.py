from flask import Flask, jsonify, request
import os
import json
import subprocess
from typing import Dict, List, Optional, Any, Union

app = Flask(__name__)

# Configuration
R_SCRIPT_DIR = os.path.join(os.path.dirname(__file__), 'r')

# --- Helper Functions (imported from act_core) ---
from act_core import (
    lookup_epa,
    create_event,
    compute_transient_impressions,
    compute_deflection,
    init_conversation,
    step_conversation,
    search_labels,
    compute_optimal_behavior,
    compute_modified_identity,
    compute_transients,
    compute_emotions,
    compute_reidentify,
    find_closest_term
)

# Note: _run_r_script is internal to act_core now, but if needed locally it can be imported.
# It seems app.py endpoints don't call it directly except in api_dictionaries which duplicates logic.
# I will fix api_dictionaries to use a new function in act_core if possible, or just leave it for now.
# api_dictionaries uses subprocess directly in the original code, BUT closely resembles _run_r_script.
# For now, I'll leave api_dictionaries as is (it uses subprocess directly) or improved.
# Wait, api_dictionaries (Line 284) uses subprocess manually.



# --- Flask Endpoints ---

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "running", 
        "service": "act-r-runtime",
        "endpoints": {
            "GET /health": "Service health status",
            "GET /r-check": "R environment and package verification",
            "GET /act/dictionaries": "List available ACT dictionaries",
            "GET /act/labels": "Search for terms in a dictionary (params: dictionary, search)",
            "POST /act/lookup": "Resolve EPA values for a term",
            "POST /act/init": "Initialize conversation state",
            "POST /act/step": "Execute simulation step",
            "POST /act/optimize": "Calculate optimal behavior",
            "POST /act/modify": "Calculate modified identity (amalgamation)",
            "POST /act/deflection": "Calculate deflection between fundamentals and transients",
            "POST /act/transients": "Calculate transient impressions after an event",
            "POST /act/emotions": "Predict emotional response",
            "POST /act/reidentify": "Calculate reidentified EPA to reduce deflection",
            "POST /act/closest": "Find closest dictionary term to an EPA vector"
        }
    }), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "act-r-runtime"}), 200

@app.route('/r-check', methods=['GET'])
def r_check():
    try:
        # 1. Check R version
        version_result = subprocess.run(
            ["Rscript", "--version"],
            capture_output=True, 
            text=True
        )
        version_info = version_result.stderr.strip() or version_result.stdout.strip()
        
        # 2. Check Packages using Rscript and jsonlite
        # We check: actdata, inteRact, bayesactR
        packages_to_check = ["actdata", "inteRact", "bayesactR"]
        pkg_vec_str = ", ".join([f"'{p}'" for p in packages_to_check])
        
        # R code to check packages and return JSON
        r_code = (
            f"pkgs <- c({pkg_vec_str}); "
            "results <- sapply(pkgs, function(p) require(p, character.only=TRUE, quiet=TRUE)); "
            "cat(jsonlite::toJSON(results, auto_unbox=TRUE))"
        )
        
        pkg_result = subprocess.run(
            ["Rscript", "-e", r_code],
            capture_output=True,
            text=True
        )
        
        if pkg_result.returncode != 0:
             raise RuntimeError(f"Package check failed: {pkg_result.stderr}")
             
        packages_status = json.loads(pkg_result.stdout.strip())
        
        # Determine overall status
        if isinstance(packages_status, list):
            # If R returned an array (lost names), zip with original keys
            packages_status = dict(zip(packages_to_check, packages_status))
            
        # 3. List available dictionaries
        r_code_dicts = (
            "library(actdata); "
            "keys <- tryCatch(sapply(actdata::get_dicts(), function(x) x@key), error=function(e) NULL); "
            "cat(jsonlite::toJSON(keys, auto_unbox=TRUE))"
        )
        
        dict_result = subprocess.run(
            ["Rscript", "-e", r_code_dicts],
            capture_output=True,
            text=True
        )
        
        dictionaries = []
        if dict_result.returncode == 0:
            try:
                dictionaries = json.loads(dict_result.stdout.strip())
            except:
                dictionaries = ["error_parsing_dictionaries"]
                
        all_installed = all(packages_status.values())
        status = "success" if all_installed else "warning"
        
        return jsonify({
            "status": status, 
            "r_version": version_info,
            "packages": packages_status,
            "dictionaries": dictionaries
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/act/dictionaries', methods=['GET'])
def api_dictionaries():
    """List available ACT dictionaries."""
    try:
        r_code_dicts = (
            "library(actdata); "
            "keys <- tryCatch(sapply(actdata::get_dicts(), function(x) x@key), error=function(e) NULL); "
            "cat(jsonlite::toJSON(keys, auto_unbox=TRUE))"
        )
        
        dict_result = subprocess.run(
            ["Rscript", "-e", r_code_dicts],
            capture_output=True,
            text=True
        )
        
        dictionaries = []
        if dict_result.returncode == 0:
            try:
                dictionaries = json.loads(dict_result.stdout.strip())
            except:
                dictionaries = ["error_parsing_dictionaries"]
        else:
             raise RuntimeError(f"R script failed: {dict_result.stderr}")

        return jsonify({"dictionaries": dictionaries}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/act/lookup', methods=['POST'])
def api_lookup():
    data = request.json
    label = data.get('label')
    type_ = data.get('type')
    dictionary = data.get('dictionary', 'us_2015')
    
    if not label or not type_:
        return jsonify({"error": "Missing 'label' or 'type'"}), 400
        
    try:
        result = lookup_epa(label, type_, dictionary)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/act/init', methods=['POST'])
def api_init():
    data = request.json
    actor = data.get('actor')
    object_ = data.get('object')
    dictionary = data.get('dictionary', 'us_2015')
    
    if not actor or not object_:
        return jsonify({"error": "Missing 'actor' or 'object'"}), 400
        
    try:
        result = init_conversation(actor, object_, dictionary)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/act/step', methods=['POST'])
def api_step():
    data = request.json
    state = data.get('state')
    behavior = data.get('behavior')
    
    if not state or not behavior:
        return jsonify({"error": "Missing 'state' or 'behavior'"}), 400
        
    try:
        result = step_conversation(state, behavior)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/act/labels', methods=['GET'])
def api_labels():
    dictionary = request.args.get('dictionary')
    search = request.args.get('search')
    
    if not dictionary:
        return jsonify({"error": "Missing 'dictionary' parameter"}), 400
        
    try:
        result = search_labels(dictionary, search)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/act/optimize', methods=['POST'])
def api_optimize():
    data = request.json
    actor = data.get('actor')
    object_ = data.get('object')
    dictionary = data.get('dictionary', 'us_2015')
    
    if not actor or not object_:
        return jsonify({"error": "Missing 'actor' or 'object'"}), 400
        
    try:
        result = compute_optimal_behavior(actor, object_, dictionary)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/act/modify', methods=['POST'])
def api_modify():
    data = request.json
    modifier = data.get('modifier')
    identity = data.get('identity')
    dictionary = data.get('dictionary', 'us_2015')
    
    if not modifier or not identity:
        return jsonify({"error": "Missing 'modifier' or 'identity'"}), 400
        
    try:
        result = compute_modified_identity(modifier, identity, dictionary)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Helper functions are imported from act_core



@app.route('/act/deflection', methods=['POST'])
def api_deflection():
    data = request.json
    fundamentals = data.get('fundamentals')
    transients = data.get('transients')
    
    if not fundamentals or not transients:
        return jsonify({"error": "Missing 'fundamentals' or 'transients'"}), 400
        
    try:
        result = compute_deflection(fundamentals, transients)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/act/transients', methods=['POST'])
def api_transients():
    data = request.json
    actor = data.get('actor')
    behavior = data.get('behavior')
    obj = data.get('object')
    dictionary = data.get('dictionary', 'us2010')
    
    if not actor or not behavior or not obj:
        return jsonify({"error": "Missing 'actor', 'behavior', or 'object'"}), 400
        
    try:
        result = compute_transients(actor, behavior, obj, dictionary)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/act/emotions', methods=['POST'])
def api_emotions():
    data = request.json
    actor = data.get('actor')
    behavior = data.get('behavior')
    obj = data.get('object')
    dictionary = data.get('dictionary', 'us2010')
    
    if not actor or not behavior or not obj:
        return jsonify({"error": "Missing 'actor', 'behavior', or 'object'"}), 400
        
    try:
        result = compute_emotions(actor, behavior, obj, dictionary)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/act/reidentify', methods=['POST'])
def api_reidentify():
    data = request.json
    actor = data.get('actor')
    behavior = data.get('behavior')
    obj = data.get('object')
    element = data.get('element', 'actor')
    dictionary = data.get('dictionary', 'us2010')
    
    if not actor or not behavior or not obj:
        return jsonify({"error": "Missing 'actor', 'behavior', or 'object'"}), 400
        
    try:
        result = compute_reidentify(actor, behavior, obj, element, dictionary)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/act/closest', methods=['POST'])
def api_closest():
    data = request.json
    epa = data.get('epa')
    term_type = data.get('type', 'identity')
    dictionary = data.get('dictionary', 'us2010')
    n = data.get('n', 5)
    
    if not epa:
        return jsonify({"error": "Missing 'epa'"}), 400
        
    try:
        result = find_closest_term(epa, term_type, dictionary, n)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

