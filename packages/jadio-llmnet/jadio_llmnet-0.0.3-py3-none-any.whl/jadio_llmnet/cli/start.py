import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
import uvicorn

CONFIG_PATH = Path.cwd() / "jadio_config" / "llmnet_config.json"

app = FastAPI(title="LLMNet LAN Server", description="Manages local model assignments and ports.")


def load_config():
    """Load llmnet_config.json from jadio_config folder."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"❌ Config file not found at {CONFIG_PATH}. Did you run 'llmnet init'?")
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"❌ Invalid JSON in llmnet_config.json: {e}")


def get_server_port(config):
    """Returns the port to run the server on."""
    return config.get("port", 47600)


@app.get("/status")
def get_status():
    """
    Get current server status.
    Returns the entire config (safe for LAN introspection).
    """
    try:
        config = load_config()
        return {
            "status": "LLMNet server is running",
            "config": config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"message": "LLMNet LAN Server. See /status."}


def run_server():
    """
    Entry point to start the server.
    Reads config, chooses port, starts FastAPI via uvicorn.
    """
    try:
        config = load_config()
        port = get_server_port(config)
        print(f"✅ Loaded configuration from {CONFIG_PATH}")
        print(f"⚡️ Starting LLMNet server on port {port}...")
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
