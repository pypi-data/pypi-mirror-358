import httpx
from ..ws.base import BaseWebSocket
from ..models.conversation import ConversationCreateResponse, ConversationInfo
from typing import Optional, Literal

class ConversationAPI:
    def __init__(self, client):
        self.client = client

    def create(self, initial_user_msg=None, image_urls=None, file_urls=None):
        payload = {
            "initial_user_msg": initial_user_msg,
            "image_urls": image_urls or [],
            "file_urls": file_urls or []
        }
        resp = httpx.post(f"{self.client.api_url}/api/conversations", json=payload, headers=self.client.headers, timeout=60)
        resp.raise_for_status()
        return ConversationCreateResponse(**resp.json())

    def get_conversation(self, conversation_id: str) -> 'ConversationInfo | None':
        url = f"{self.client.api_url}/api/conversations/{conversation_id}"
        resp = httpx.get(url, headers=self.client.headers, timeout=30)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return ConversationInfo(**resp.json())

    def get_trajectory_v2(self, conversation_id: str, cursor: Optional[str] = None, per_page: int = 50, direction: Literal["next", "previous"] = "next") -> dict:
        url = f"{self.client.api_url}/api/v2/conversations/{conversation_id}/trajectory"
        params = {"per_page": per_page, "direction": direction}
        if cursor:
            params["cursor"] = cursor
        resp = httpx.get(url, headers=self.client.headers, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def ws_connect(self, conversation_id, on_message):
        ws_url = f"{self.client.ws_url}/ws/conversation/{conversation_id}"
        return BaseWebSocket(ws_url, self.client.api_key, on_message)
