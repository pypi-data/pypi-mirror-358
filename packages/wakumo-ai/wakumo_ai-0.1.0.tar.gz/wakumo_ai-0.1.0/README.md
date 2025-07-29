# Wakumo AI CLI & Python SDK

A modern Python library and CLI tool to interact with the Wakumo AI backend (API & WebSocket).

---

## Features
- Interact with Wakumo AI backend via REST API and WebSocket
- Unified authentication (WAKUMO_API_KEY)
- Modular, extensible structure for all API logic (conversation, file, ...)
- Usable as both a Python library and a CLI tool

---

## Installation

### 1. Install Poetry (if not already installed)
```bash
pip install poetry
```

### 2. Install dependencies
```bash
poetry install
```

### 3. (Optional) Activate Poetry virtual environment
```bash
poetry shell
```

---

## Configuration

Set your API key and endpoint (via environment variable or .env file):

```env
WAKUMO_API_KEY=your_api_key_here
WAKUMO_API_URL=https://api.wakumo.ai
WAKUMO_WS_URL=wss://api.wakumo.ai
```

---

## Usage as Python Library

### 1. Create a conversation (REST API)
```python
from wakumo_ai import WakumoAIClient

client = WakumoAIClient()  # Auto-loads config from env/.env

response = client.conversation.create(
    selected_repository="username/repo",
    selected_branch="main",
    initial_user_msg="Hello, let's start!",
    image_urls=[]
)
print("Conversation created:", response.conversation_id)
```

### 2. Listen to conversation events (WebSocket)
```python
from wakumo_ai import WakumoAIClient

client = WakumoAIClient()
def on_message(event):
    print("New event:", event)

ws = client.conversation.ws_connect(conversation_id="abc123", on_message=on_message)
ws.run_forever()
```

---

## Usage as CLI

```bash
wakumo-ai conversation create --repo "username/repo" --branch "main" --msg "Hello"
wakumo-ai conversation listen --id abc123
```

---

## Project Structure

```
wakumo_ai/
├── __init__.py                # WakumoAIClient, public API
├── cli.py                     # CLI entrypoint
├── config.py                  # Config management
├── exceptions.py              # Custom exceptions
├── utils.py                   # Utilities
│
├── api/
│   ├── __init__.py
│   ├── conversation.py        # ConversationAPI: REST + ws_connect
│   ├── file.py                # FileAPI: REST + ws_connect
│   └── ...
│
├── ws/
│   ├── __init__.py
│   └── base.py                # BaseWebSocket logic
│
├── models/
│   ├── __init__.py
│   ├── conversation.py
│   └── ...
│
├── commands/
│   ├── __init__.py
│   ├── conversation.py        # CLI commands
│   └── ...
└── auth.py                    # Auth logic
```

---

## Testing

```bash
poetry run pytest
```

---

## License
MIT

```