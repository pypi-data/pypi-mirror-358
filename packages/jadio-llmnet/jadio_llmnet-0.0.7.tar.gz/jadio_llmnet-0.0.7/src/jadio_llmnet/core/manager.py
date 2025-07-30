import json
from pathlib import Path

CONFIG_DIR = Path.cwd() / "jadio_config"
GLOBAL_CONFIG = CONFIG_DIR / "llmnet_config.json"

def get_current_user_config_path():
    """Get the config path for the currently logged in user"""
    if not GLOBAL_CONFIG.exists():
        return CONFIG_DIR / "llmnet_config.json"  # Fallback to default
    
    with open(GLOBAL_CONFIG, "r") as f:
        global_data = json.load(f)
    
    current_user = global_data.get("current_account")
    if current_user:
        user_config = CONFIG_DIR / f"llmnet_config_{current_user}.json"
        if user_config.exists():
            return user_config
    
    # Fallback to default config
    return CONFIG_DIR / "llmnet_config.json"

def load_config():
    config_path = get_current_user_config_path()
    if not config_path.exists():
        raise FileNotFoundError("Config not found. Did you run 'llmnet init'?")
    with config_path.open(encoding="utf-8") as f:
        return json.load(f)

def save_config(config):
    config_path = get_current_user_config_path()
    with config_path.open("w", encoding="utf-8") as f:
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