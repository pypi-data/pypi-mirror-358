import sys
import importlib

COMMANDS = {
    "init": "init",
    "login": "login",
    "logout": "logout",
    "status": "status",
    "add": "add",
    "remove": "remove",
    "start": "start",  # Add this line
    "stop": "stop",
    "persist": "persist",
    "name": "name",
    "account": "account"
}

def print_help():
    print("""
LLMNet CLI

Usage:
  llmnet <command> [options]

Available Commands:
  init              Initialize llmnet configuration
  login             Log in to LLMNet
  logout            Log out of LLMNet
  status            View assigned models and ports
  add               Add a model to a port
  remove            Remove a model from a port
  start             Start the LLMNet server
  stop              Stop the LLMNet server
  persist           Enable or disable persistence
  name              Rename an assigned model
  account           Manage accounts (show, create, change-pw)

Examples:
  llmnet init
  llmnet login
  llmnet start
  llmnet add
  llmnet remove
  llmnet account create
""")

def main():
    if len(sys.argv) < 2:
        print("❌ No command provided.\n")
        print_help()
        return

    cmd = sys.argv[1].lower()

    if cmd not in COMMANDS:
        print(f"❌ Unknown command: {cmd}\n")
        print_help()
        return

    try:
        # Dynamically import CLI module
        module_path = f"jadio_llmnet.cli.{COMMANDS[cmd]}"
        cli_module = importlib.import_module(module_path)
        cli_args = sys.argv[2:]
        cli_module.run(cli_args)
    except Exception as e:
        print(f"❌ Error running command '{cmd}': {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()