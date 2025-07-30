# core/manager.py

import subprocess
import shutil
import os
from typing import Dict, Any

RUNNING_PROCESSES: Dict[str, subprocess.Popen] = {}

# Helper to find a free port
def get_free_port(config: dict) -> int:
    used_ports = {m["assigned_port"] for m in config["models"]}
    start, end = config["port_range"]
    for port in range(start, end + 1):
        if port not in used_ports:
            return port
    raise ValueError("No free ports available in configured range.")

# List all models
def list_models(config: dict):
    return config["models"]

# Add new model
def add_model(config: dict, name: str, path: str, backend: str) -> dict:
    for model in config["models"]:
        if model["name"] == name:
            return {"success": False, "message": "Model name already exists."}

    if not os.path.exists(path):
        return {"success": False, "message": "Model file path does not exist."}

    try:
        assigned_port = get_free_port(config)
    except ValueError as e:
        return {"success": False, "message": str(e)}

    new_model = {
        "name": name,
        "path": path,
        "backend": backend,
        "assigned_port": assigned_port,
        "status": "stopped"
    }
    config["models"].append(new_model)
    return {"success": True, "message": f"Model {name} added on port {assigned_port}."}

# Remove model
def remove_model(config: dict, name: str) -> dict:
    for idx, model in enumerate(config["models"]):
        if model["name"] == name:
            stop_model(config, name)  # Stop if running
            del config["models"][idx]
            return {"success": True, "message": f"Removed model {name}."}
    return {"success": False, "message": "Model not found."}

# Start model
def start_model(config: dict, name: str) -> dict:
    for model in config["models"]:
        if model["name"] == name:
            if name in RUNNING_PROCESSES:
                return {"success": False, "message": "Model is already running."}

            # Example: replace with your real backend launch command
            cmd = build_backend_command(model)
            if not cmd:
                return {"success": False, "message": "Unsupported backend type."}

            try:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                RUNNING_PROCESSES[name] = process
                model["status"] = "running"
                return {"success": True, "message": f"Model {name} started on port {model['assigned_port']}."}
            except Exception as e:
                return {"success": False, "message": f"Failed to start model: {str(e)}"}

    return {"success": False, "message": "Model not found."}

# Stop model
def stop_model(config: dict, name: str) -> dict:
    if name in RUNNING_PROCESSES:
        proc = RUNNING_PROCESSES[name]
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        del RUNNING_PROCESSES[name]

    for model in config["models"]:
        if model["name"] == name:
            model["status"] = "stopped"
            return {"success": True, "message": f"Model {name} stopped."}
    return {"success": False, "message": "Model not found."}

# Rename model
def rename_model(config: dict, old_name: str, new_name: str) -> dict:
    for model in config["models"]:
        if model["name"] == old_name:
            model["name"] = new_name
            if old_name in RUNNING_PROCESSES:
                RUNNING_PROCESSES[new_name] = RUNNING_PROCESSES.pop(old_name)
            return {"success": True, "message": f"Model renamed to {new_name}."}
    return {"success": False, "message": "Model not found."}

# Build actual launch command per backend
def build_backend_command(model: Dict[str, Any]) -> list:
    backend = model["backend"]
    port = model["assigned_port"]
    path = model["path"]

    if backend == "llamacpp":
        # Example placeholder command; replace with actual llama.cpp server call
        return [
            "python", "llama_server.py",
            "--model", path,
            "--port", str(port)
        ]

    # Add more backends here
    return None
