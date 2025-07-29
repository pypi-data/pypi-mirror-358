import websocket
import threading

class BaseWebSocket:
    def __init__(self, ws_url, api_key, on_message):
        self.ws_url = ws_url
        self.api_key = api_key
        self.on_message = on_message
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            header=[f"Authorization: Bearer {self.api_key}"],
            on_message=lambda ws, msg: self.on_message(msg)
        )

    def run_forever(self):
        thread = threading.Thread(target=self.ws.run_forever)
        thread.daemon = True
        thread.start()
        thread.join()