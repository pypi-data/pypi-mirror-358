import httpx
from ..ws.base import BaseWebSocket
from ..models.conversation import ConversationCreateResponse, ConversationInfo

class ConversationAPI:
    def __init__(self, client):
        self.client = client

    def create(self, selected_repository=None, selected_branch=None, initial_user_msg=None, image_urls=None):
        payload = {
            "selected_repository": selected_repository,
            "selected_branch": selected_branch,
            "initial_user_msg": initial_user_msg,
            "image_urls": image_urls or []
        }
        resp = httpx.post(f"{self.client.api_url}/api/conversations", json=payload, headers=self.client.headers, timeout=10)
        resp.raise_for_status()
        return ConversationCreateResponse(**resp.json())

    def get_conversation(self, conversation_id: str, include_events: bool = False) -> 'ConversationInfo | None':
        url = f"{self.client.api_url}/api/conversations/{conversation_id}"
        params = {"include_events": str(include_events).lower()}
        resp = httpx.get(url, headers=self.client.headers, params=params, timeout=10)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return ConversationInfo(**resp.json())

    def ws_connect(self, conversation_id, on_message):
        ws_url = f"{self.client.ws_url}/ws/conversation/{conversation_id}"
        return BaseWebSocket(ws_url, self.client.api_key, on_message)