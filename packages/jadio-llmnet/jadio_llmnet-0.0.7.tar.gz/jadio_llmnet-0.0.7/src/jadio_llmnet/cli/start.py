import json
import os
from pathlib import Path
from multiprocessing import Process
import time

CONFIG_DIR = Path.cwd() / "jadio_config"
PID_FILE = CONFIG_DIR / "llmnet.pid"

def run(args=None):
    """Start the LLMNet server"""
    print("⚡️ Starting LLMNet Server...\n")
    
    # Check if server is already running
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            # Check if process is actually running
            os.kill(pid, 0)
            print("❌ LLMNet server is already running (PID: {})".format(pid))
            return
        except (ProcessLookupError, ValueError):
            # Process not running or invalid PID, clean up
            PID_FILE.unlink()
    
    # Import here to avoid circular imports
    from jadio_llmnet.core.server import run_server
    
    # Start server in a subprocess
    try:
        # Fork process on Unix-like systems
        if hasattr(os, 'fork'):
            pid = os.fork()
            if pid > 0:
                # Parent process
                PID_FILE.write_text(str(pid))
                print(f"✅ LLMNet server started in background (PID: {pid})")
                print("📡 Use 'llmnet stop' to stop the server")
                return
            else:
                # Child process
                run_server()
        else:
            # Windows doesn't support fork, use multiprocessing
            from multiprocessing import Process
            server_process = Process(target=run_server)
            server_process.start()
            
            # Write PID
            PID_FILE.write_text(str(server_process.pid))
            print(f"✅ LLMNet server started (PID: {server_process.pid})")
            print("📡 Use 'llmnet stop' to stop the server")
            print("⚠️  On Windows, the server runs in foreground. Use Ctrl+C to stop.")
            
            # On Windows, we need to keep the parent alive
            try:
                server_process.join()
            except KeyboardInterrupt:
                server_process.terminate()
                PID_FILE.unlink()
                print("\n✅ Server stopped.")
    
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()