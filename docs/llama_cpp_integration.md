# Setting up llama.cpp integration

### 1. Start llama.server

You need a running `llama.cpp` server. We recommend using a pre-built package from [llama.cpp releases](https://github.com/ggml-org/llama.cpp/releases/latest).

```bash
# Download and extract llama.cpp
wget https://github.com/ggml-org/llama.cpp/releases/download/b9124/llama-b9124-bin-ubuntu-x64.tar.gz
tar xf llama-b9124-bin-ubuntu-x64.tar.gz
cd llama-b9124

# Start the server with a model (e.g., GPT OSS 20B)
./llama-server -hf ggml-org/gpt-oss-20b-GGUF --port 8001
```

The Web UI will be available at `http://localhost:8001`.

![webui](docs/img/llama_server_webui.png)

### 2. Add MCP Server to llama.cpp

1. In the llama.cpp Web UI, navigate to **MCP Servers**.
2. Click **+ Add New Server**.
3. Enter the URL: `http://localhost:8000/mcp`.

![mcpserver](docs/img/llama_server_mcp_servers.png)

### 3. Test the server

Start a new chat and ensure the SuperTrader server is enabled. Ask for the current price of a stock (e.g., "What is the price of NVDA?").

![newchat](docs/img/llama_server_new_chat.png)
![nvdaprice](docs/img/llama_server_nvidia_price.png)
