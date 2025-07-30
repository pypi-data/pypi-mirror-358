from jadio_llmnet.core import manager

def run(args=None):
    print("⚡️ LLMNet REMOVE\n")

    # 1️⃣ Enforce authentication
    if not manager.is_logged_in():
        print("❌ You must be logged in to remove a model assignment.")
        return

    # 2️⃣ Prompt for port
    try:
        port_input = input("Enter port number to unassign: ").strip()
        port = int(port_input)
    except ValueError:
        print("❌ Invalid port number.")
        return

    # 3️⃣ Attempt unassignment
    try:
        manager.unassign_model(port)
        print(f"✅ Port {port} unassigned successfully.")
    except Exception as e:
        print(f"❌ Failed to unassign port {port}: {e}")
