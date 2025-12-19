import asyncio
import json
import websockets

class ControlClient:
    def __init__(self, url, token, session_id):
        self.url = url
        self.token = token
        self.session_id = session_id
        self.ws = None
        self._recv_task = None
        self.audio_ready = asyncio.Event()

    async def connect(self):
        self.ws = await websockets.connect(
            self.url,
            additional_headers={
                "Authorization": f"Bearer {self.token}",
                "X-Session-Id": self.session_id,
            },
            ping_interval=20,
            ping_timeout=20,
        )
        await self._send("session.start", {})
        self._recv_task = asyncio.create_task(self._recv_loop())

    async def close(self):
        if self.ws:
            await self._send("session.stop", {})
            await self.ws.close()
        if self._recv_task:
            self._recv_task.cancel()

    async def send_chat(self, content):
        await self._send("chat.message", {"content": content})

    async def send_command(self, name, payload=None):
        await self._send("command", {
            "name": name,
            "payload": payload or {}
        })

    async def _send(self, event, data):
        msg = {
            "event": event,
            "data": data,
        }
        await self.ws.send(json.dumps(msg))

    async def _recv_loop(self):
        try:
            async for raw in self.ws:
                msg = json.loads(raw)
                await self.handle_event(msg)
        except asyncio.CancelledError:
            pass

    async def negotiate(self):
        await self._send("capabilities.advertise", {
            "transports": ["ws"],
            "modalities": ["audio"],
            "codecs": ["opus"],
            "protocols": ["ws-audio-v1"],
        })

    async def handle_event(self, msg):
        event = msg.get("event")
        data = msg.get("data")

        if event == "capabilities.accept":
            await self.on_capabilities_accepted(data)
        elif event == "capabilities.reject":
            await self.on_capabilities_rejected(data)
        elif event == "chat.reply":
            await self.on_chat_reply(data)
        elif event == "error":
            await self.on_error(data)

    async def on_capabilities_accepted(self, data):
        self.audio_url = data["endpoints"].get("audio")
        self.protocol = data.get("protocol")

        if self.audio_url:
            self.audio_ready.set()
            await self.start_audio(self.audio_url)

    async def on_capabilities_rejected(self, data):
        pass

    async def on_chat_reply(self, data):
        pass

    async def on_error(self, data):
        pass
