import logging
import subprocess
import discord
from config.api import APIConfig
import asyncio
from discord.ext import voice_recv
import numpy as np
import soxr
from utils.rtp import RTPPacket
from services.server_websockets import WebSocketClient
from contextlib import suppress
from config.settings import SERVER_SAMPLERATE
from utils.utils import mono_to_stereo, stereo_to_mono

class DiscordIO:
    def __init__(self):
        self.server = WebSocketClient(APIConfig.CONNECT)
        self.vc_client: voice_recv.VoiceRecvClient | None = None
        self.pipeline = None

        # queue with audio coming from Discord
        self.outbox: asyncio.Queue[
            tuple[discord.User, voice_recv.VoiceData]
        ] = asyncio.Queue()

        self._tasks: list[asyncio.Task] = []
        self._connected = False

    async def connect(self, channel: discord.VoiceChannel):
        """Connect to a Discord voice channel and set up the audio pipeline and server connection."""
        if self._connected:
            await self.disconnect()
        self._connected = True

        # connect to Discord
        self.vc_client: voice_recv.VoiceRecvClient = await channel.connect(cls=voice_recv.VoiceRecvClient)
        #print("Esto nunca se imprime")
        await asyncio.sleep(0.5)

        loop = asyncio.get_running_loop()

        def async_callback(user, data): # callback from discord-ext-voice-recv
            loop.call_soon_threadsafe(
                self.outbox.put_nowait, (user, data)
            )
        self.pipeline = SoxrResampleSource()
        
        # start capturing
        self.vc_client.listen(voice_recv.BasicSink(async_callback))
        self.vc_client.play(self.pipeline)

        # connect to the WebSocket server with automatic reconnection
        await self.server.connect()
        self._tasks = [
            asyncio.create_task(self._process_audio()),
            asyncio.create_task(self._receive_audio()),
        ]
        

    async def disconnect(self): 
        """Disconnect from Discord and the server, stopping all tasks and pipelines.""" 
        if not self._connected: 
            return
        self._connected = False
        # Stop tasks
        for t in self._tasks:
            t.cancel()
            with suppress(asyncio.CancelledError):
                await t
        self._tasks.clear()
        # discord
        if self.vc_client:
            with suppress(Exception):
                self.vc_client.stop_playing()
                self.vc_client.stop_listening()
                await self.vc_client.disconnect()
        if self.pipeline:
            with suppress(Exception):
                self.pipeline.cleanup()
                self.pipeline = None
        # server
        with suppress(Exception):
            await self.server.close()

    async def _process_audio(self):
        # Crear el resampler incremental (48k → 24k)
        resampler = soxr.ResampleStream(
            num_channels=1,
            in_rate=48000,
            out_rate=SERVER_SAMPLERATE,
            dtype=np.int16,
            quality='VHQ'
        )
        while self._connected:
            user, data = await self.outbox.get()
            try:
                stereo_48k = np.frombuffer(data.pcm, dtype=np.int16)
                mono_48k = stereo_to_mono(stereo_48k)

                mono_24k = resampler.resample_chunk(mono_48k)

                if mono_24k.size == 0:
                    continue

                packet = RTPPacket(
                    payload_type=121,
                    payload=mono_24k.tobytes()
                )
                await self.server.send(packet.to_bytes())

            except Exception as e:
                print(f"[DiscordIO] Error procesando audio: {e}")
            finally:
                self.outbox.task_done()


    async def _receive_audio(self):
        """Loop receiving audio from the server and sending it with the pipeline to Discord."""

        async for raw in self.server.recv_stream():
            if not self._connected:
                break
            try:
                packet = RTPPacket.from_bytes(raw)
                if not packet.is_audio():
                    continue

                if self.pipeline:
                    self.pipeline.push_chunk(packet.payload)

            except Exception as e:
                print(f"[DiscordIO] Error recibiendo audio: {e}")



class SoxrResampleSource(discord.AudioSource):
    def __init__(self):
        self.inbuf = bytearray()   # 24 kHz mono PCM que entra del servidor
        self.outbuf = bytearray()  # 48 kHz stereo PCM para Discord
        # rellenar con 4 segundos de silencio
        self.resampler = soxr.ResampleStream(
            num_channels=1,
            in_rate=SERVER_SAMPLERATE,
            out_rate=48000,
            dtype=np.int16,
            quality='VHQ'
        )

    def is_opus(self):
        return False

    def push_chunk(self, chunk: bytes):
        # acumular lo que llegó
        self.inbuf.extend(chunk)

        # garantizar múltiplos de 2 bytes (int16)
        usable = (len(self.inbuf) // 2) * 2
        if usable == 0:
            return
        raw = self.inbuf[:usable]
        del self.inbuf[:usable]

        x = np.frombuffer(raw, dtype=np.int16)

        # resample: 24 kHz → 48 kHz
        y = self.resampler.resample_chunk(x)

        y_st = mono_to_stereo(y)

        self.outbuf.extend(y_st.tobytes())

    def read(self):
        frame_size = 3840  # 20ms @48kHz stereo

        if len(self.outbuf) < frame_size:
            return b'\x00' * frame_size

        out = bytes(self.outbuf[:frame_size])
        del self.outbuf[:frame_size]
        return out

