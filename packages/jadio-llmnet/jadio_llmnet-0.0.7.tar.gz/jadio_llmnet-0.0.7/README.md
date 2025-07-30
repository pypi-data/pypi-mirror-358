# LLMNet

LLMNet is a local LAN server for **configuring, assigning, and hot-swapping** local language models on your own network.

It’s designed to help you manage your local AI deployments with ease, providing a single interface to load, unload, and switch between "lazy" local models on demand.

---

## 🚀 About

LLMNet makes it easy to build your own **Local Model Hub**:

- Assign models to specific ports on your local machine or LAN.
- Lazy-load large models only when needed.
- Hot-swap models without restarting the whole server.
- Enable local devices or apps on your network to query any assigned model.
- Avoid relying on cloud APIs for privacy, cost, or latency reasons.

LLMNet is ideal for anyone running multiple local AI models and wanting an easy, organized way to manage them across their LAN.

---

## ⚙️ Key Features

✅ Local server that runs on your LAN  
✅ Configurable ports and model assignments  
✅ Lazy loading for efficient memory use  
✅ Hot-swap models with zero downtime  
✅ Simple CLI to manage everything  
✅ Designed for self-hosting and privacy  

---

## 📦 Example Use Cases

- Run multiple LLMs on one machine and assign them to different ports.
- Let local apps choose which model they want to call.
- Easily test and compare models by swapping assignments.
- Share models across devices on your local network securely.
- Build your own "local huggingface" with your own models.

---

## 🗂️ How It Works

1. **Start the server**  
   - Runs on your machine or server on a designated LAN port.
2. **Assign models to ports**  
   - Use the CLI to load models and map them to specific ports.
3. **Lazy load on demand**  
   - Models load into memory only when first called.
4. **Hot-swap at any time**  
   - Change model assignments without restarting the server.
5. **Connect over LAN**  
   - Local devices or apps can send requests to specific models via their assigned ports.

---

## 🛠️ Planned Features

- Web-based admin panel for managing assignments  
- Resource monitoring (CPU, GPU, RAM) per model  
- User authentication and access control  
- Preset configuration profiles  
- Model performance and latency metrics  
- Support for ONNX, GGUF, SafeTensors, and other formats

---

## 🗺️ Project Goals

LLMNet aims to make **local model management** as easy as:

- Plug and play
- Secure and private
- Cost-effective
- Cloud-independent

If you want to build your own *mini OpenAI-style service* for local models, LLMNet is your foundation.

---

## 💼 License

MIT License

---

## ✨ Build your own Local Model Hub. Stay in control. Use LLMNet. 🚀

