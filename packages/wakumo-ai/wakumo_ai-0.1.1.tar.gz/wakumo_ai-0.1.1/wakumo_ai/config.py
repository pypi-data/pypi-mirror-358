import os
from dotenv import load_dotenv
from wakumo_ai.log import vprint

load_dotenv()

def _mask_api_key(api_key):
    if not api_key or len(api_key) < 8:
        return api_key
    return f"{api_key[:4]}...{api_key[-4:]}"

def get_api_key():
    api_key = os.getenv('WAKUMO_API_KEY')
    vprint(f"[wakumo_ai.config] WAKUMO_API_KEY: {_mask_api_key(api_key)}")
    return api_key

def get_api_url():
    api_url = os.getenv('WAKUMO_API_URL', 'https://api.wakumo.ai')
    vprint(f"[wakumo_ai.config] WAKUMO_API_URL: {api_url}")
    return api_url

def get_ws_url():
    ws_url = os.getenv('WAKUMO_WS_URL', 'wss://api.wakumo.ai')
    vprint(f"[wakumo_ai.config] WAKUMO_WS_URL: {ws_url}")
    return ws_url