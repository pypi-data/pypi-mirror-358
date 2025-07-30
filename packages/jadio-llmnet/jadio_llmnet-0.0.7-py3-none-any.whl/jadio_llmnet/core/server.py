import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

CONFIG_PATH = Path.cwd() / "jadio_config" / "llmnet_config.json"

app = FastAPI(
    title="LLMNet LAN Server",
    description="Manage local AI model assignments and ports.",
    version="0.1.0"
)


#
# === CONFIG HELPERS ===
#

def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}. Please run 'llmnet init'.")
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def save_config(config):
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def get_server_port(config):
    return config.get("port", 47600)


#
# === Pydantic models for requests ===
#

class AssignRequest(BaseModel):
    port: int
    model: str
    path: str
    lazy: bool = True


class UnassignRequest(BaseModel):
    port: int


#
# === ROUTES ===
#

@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/status")
def get_status():
    try:
        config = load_config()
        return {
            "status": "LLMNet server is running",
            "assigned": config.get("assigned", {}),
            "locked_ports": config.get("locked_ports", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/assign")
def assign_model(request: AssignRequest):
    try:
        config = load_config()

        if request.port not in config.get("locked_ports", []):
            raise HTTPException(status_code=400, detail=f"Port {request.port} is not locked/available.")

        if str(request.port) in config.get("assigned", {}):
            raise HTTPException(status_code=400, detail=f"Port {request.port} is already assigned.")

        # Add assignment
        config.setdefault("assigned", {})[str(request.port)] = {
            "model": request.model,
            "path": request.path,
            "lazy": request.lazy
        }

        save_config(config)
        return {"message": f"Model '{request.model}' assigned to port {request.port}."}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/unassign")
def unassign_model(request: UnassignRequest):
    try:
        config = load_config()

        if str(request.port) not in config.get("assigned", {}):
            raise HTTPException(status_code=400, detail=f"Port {request.port} is not assigned.")

        # Remove assignment
        del config["assigned"][str(request.port)]

        save_config(config)
        return {"message": f"Port {request.port} unassigned successfully."}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"message": "Welcome to LLMNet LAN Server. Use /status, /assign, /unassign."}


#
# === ENTRY POINT ===
#

def run_server():
    try:
        config = load_config()
        port = get_server_port(config)
        print(f"✅ Loaded configuration from {CONFIG_PATH}")
        print(f"⚡️ Starting LLMNet server on port {port}...")
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
