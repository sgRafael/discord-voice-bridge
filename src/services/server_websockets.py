import asyncio
import websockets

class WebSocketClient:
    """WebSocket client con streaming y reconexión automática mínima segura."""

    def __init__(self, uri: str, retry_delay: float = 1.0):
        self.uri = uri
        self.conn: websockets.WebSocketClientProtocol | None = None
        self.retry_delay = retry_delay
        self._lock = asyncio.Lock()
        self._running = False

    async def connect(self):
        """Establece la conexión inicial si no está conectada."""
        if self._running:
            return
        self._running = True
        await self._ensure_connected()

    async def _ensure_connected(self):
        """Reconecta si es necesario."""
        if self.conn:
            return
        async with self._lock:
            if self.conn:
                return
            while self._running:
                try:
                    self.conn = await websockets.connect(self.uri)
                    return
                except Exception:
                    await asyncio.sleep(self.retry_delay)

    async def _reconnect(self):
        """Fuerza la reconexión."""
        async with self._lock:
            if self.conn:
                try:
                    await self.conn.close()
                except Exception:
                    pass
            self.conn = None
            await self._ensure_connected()

    async def send(self, data: bytes):
        """Envía datos con reconexión automática."""
        while self._running:
            await self._ensure_connected()
            try:
                await self.conn.send(data)
                return
            except websockets.ConnectionClosed:
                self.conn = None
                await self._ensure_connected()
            except Exception:
                self.conn = None
                await asyncio.sleep(self.retry_delay)

    async def recv_stream(self):
        """Generador async que devuelve mensajes, reconectando si es necesario."""
        while self._running:
            await self._ensure_connected()
            try:
                msg = await self.conn.recv()
                yield msg
            except websockets.ConnectionClosed:
                self.conn = None
                await self._ensure_connected()
            except Exception:
                self.conn = None
                await asyncio.sleep(self.retry_delay)

    async def close(self):
        """Cierra la conexión y detiene los loops."""
        self._running = False
        if self.conn:
            try:
                await self.conn.close()
            except Exception:
                pass
        self.conn = None
