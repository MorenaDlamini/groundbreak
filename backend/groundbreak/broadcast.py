from fastapi import WebSocket

class Broadcaster:
    def __init__(self):
        self.clients: set[WebSocket] = set()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.clients.add(ws)

    async def disconnect(self, ws: WebSocket):
        self.clients.discard(ws)

    async def push(self, message: dict):
        dead: set[WebSocket] = set()
        for client in self.clients:
            try:
                await client.send_json(message)
            except Exception:
                dead.add(client)
        self.clients -= dead

broadcaster = Broadcaster()