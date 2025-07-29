import os
from dotenv import load_dotenv

load_dotenv()

def get_api_key():
    return os.getenv('WAKUMO_API_KEY')

def get_api_url():
    return os.getenv('WAKUMO_API_URL', 'https://api.wakumo.ai')

def get_ws_url():
    return os.getenv('WAKUMO_WS_URL', 'wss://api.wakumo.ai')