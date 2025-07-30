import json
from pathlib import Path

CONFIG_PATH = Path.cwd() / "jadio_config" / "llmnet_config.json"

def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError("llmnet_config.json not found. Did you run 'llmnet init'?")
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return json.load(f)

def save_config(config):
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

def is_logged_in():
    try:
        config = load_config()
        return config.get("logged_in", False)
    except:
        return False

def get_assignments():
    config = load_config()
    return config.get("assigned", {})

def assign_model(port: int, model: str, path: str, lazy: bool = True, name: str = None):
    config = load_config()

    port_str = str(port)
    if port not in config.get("locked_ports", []):
        raise ValueError(f"Port {port} is not in locked_ports.")
    
    if port_str in config.get("assigned", {}):
        raise ValueError(f"Port {port} is already assigned.")

    assignment = {
        "model": model,
        "path": path,
        "lazy": lazy
    }
    if name:
        assignment["name"] = name

    config.setdefault("assigned", {})[port_str] = assignment
    save_config(config)
    return assignment

def unassign_model(port: int):
    config = load_config()
    port_str = str(port)

    if port_str not in config.get("assigned", {}):
        raise ValueError(f"Port {port} is not assigned.")

    del config["assigned"][port_str]
    save_config(config)

def set_lazy(port: int, lazy: bool):
    config = load_config()
    port_str = str(port)

    if port_str not in config.get("assigned", {}):
        raise ValueError(f"Port {port} is not assigned.")

    config["assigned"][port_str]["lazy"] = lazy
    save_config(config)

def rename_model(port: int, new_name: str):
    config = load_config()
    port_str = str(port)

    if port_str not in config.get("assigned", {}):
        raise ValueError(f"Port {port} is not assigned.")

    config["assigned"][port_str]["name"] = new_name
    save_config(config)
