# core/server.py

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from . import manager, persistence

app = FastAPI(
    title="Jadio LLM LAN Server",
    description="Local service to manage ports, lazy-load models, and persist state for VS Code extension.",
    version="1.0.0"
)

# Load persistent config on startup
config = persistence.load_config()


# --- Pydantic Models for Requests ---
class AddModelRequest(BaseModel):
    name: str
    path: str
    backend: str

class NameChangeRequest(BaseModel):
    old_name: str
    new_name: str

class SimpleNameRequest(BaseModel):
    name: str


# --- API Endpoints ---

@app.get("/status")
def get_status():
    """
    Returns server health and all model statuses.
    """
    models = manager.list_models(config)
    return {"status": "ok", "models": models}


@app.get("/models")
def get_models():
    """
    Returns all registered models.
    """
    return manager.list_models(config)


@app.post("/start")
def start_model(req: SimpleNameRequest):
    """
    Starts the specified model (lazy load).
    """
    result = manager.start_model(config, req.name)
    persistence.save_config(config)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/stop")
def stop_model(req: SimpleNameRequest):
    """
    Stops the specified model.
    """
    result = manager.stop_model(config, req.name)
    persistence.save_config(config)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/add")
def add_model(req: AddModelRequest):
    """
    Registers a new model and assigns it a port.
    """
    result = manager.add_model(config, req.name, req.path, req.backend)
    persistence.save_config(config)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/remove")
def remove_model(req: SimpleNameRequest):
    """
    Unregisters a model from the system.
    """
    result = manager.remove_model(config, req.name)
    persistence.save_config(config)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/name")
def rename_model(req: NameChangeRequest):
    """
    Changes the friendly name of a model in the config.
    """
    result = manager.rename_model(config, req.old_name, req.new_name)
    persistence.save_config(config)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/persist")
def persist_config():
    """
    Forces saving current config to disk.
    """
    persistence.save_config(config)
    return {"success": True, "message": "Config saved to disk."}


# --- Entrypoint ---

def run_server():
    """
    Starts the FastAPI server for LAN.
    """
    uvicorn.run("core.server:app", host="127.0.0.1", port=5050, reload=False)


if __name__ == "__main__":
    run_server()
