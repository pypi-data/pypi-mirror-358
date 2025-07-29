from .config import get_api_key, get_api_url, get_ws_url
from .api import ConversationAPI, FileAPI

class WakumoAIClient:
    def __init__(self, api_key=None, api_url=None, ws_url=None):
        self.api_key = api_key or get_api_key()
        self.api_url = api_url or get_api_url()
        self.ws_url = ws_url or get_ws_url()
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self._conversation = None
        self._file = None

    @property
    def conversation(self) -> ConversationAPI:
        if self._conversation is None:
            self._conversation = ConversationAPI(self)
        return self._conversation

    @property
    def file(self) -> FileAPI:
        if self._file is None:
            self._file = FileAPI(self)
        return self._file