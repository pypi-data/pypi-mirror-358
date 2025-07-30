from jadio_llmnet.core import manager

def run(args=None):
    print("⚡️ LLMNet ADD\n")

    # 1️⃣ Ensure user is logged in
    if not manager.is_logged_in():
        print("❌ You must be logged in to assign a model.")
        return

    # 2️⃣ Prompt for details
    try:
        port_input = input("Enter port to assign: ").strip()
        port = int(port_input)
    except ValueError:
        print("❌ Invalid port number.")
        return

    model = input("Model name: ").strip()
    if not model:
        print("❌ Model name cannot be empty.")
        return

    path = input("Model path: ").strip()
    if not path:
        print("❌ Model path cannot be empty.")
        return

    lazy_input = input("Lazy load (y/n): ").strip().lower()
    lazy = lazy_input in ["y", "yes"]

    name_input = input("Optional friendly name (or leave blank): ").strip()
    friendly_name = name_input if name_input else None

    # 3️⃣ Call manager to assign
    try:
        assignment = manager.assign_model(
            port=port,
            model=model,
            path=path,
            lazy=lazy,
            name=friendly_name
        )
        print(f"\n✅ Model '{model}' assigned to port {port} successfully.")
    except Exception as e:
        print(f"❌ Failed to assign model: {e}")
