from jadio_llmnet.core import manager

def run(args=None):
    print("⚡️ LLMNet NAME\n")

    if not manager.is_logged_in():
        print("❌ You must be logged in to rename a model.")
        return

    try:
        port_input = input("Enter port number: ").strip()
        port = int(port_input)
    except ValueError:
        print("❌ Invalid port number.")
        return

    new_name = input("Enter new name: ").strip()
    if not new_name:
        print("❌ Name cannot be empty.")
        return

    try:
        manager.rename_model(port, new_name)
        print(f"✅ Model on port {port} renamed to '{new_name}'.")
    except Exception as e:
        print(f"❌ Failed to rename model: {e}")