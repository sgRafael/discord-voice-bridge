# Discord Voice Bot

Discord bot that connects to a speech-to-speech AI agent via WebSockets. It captures audio from Discord voice channels and plays audio back in real time using `discord-ext-voice-recv`.

Voice receive extension:
[https://github.com/imayhaveborkedit/discord-ext-voice-recv](https://github.com/imayhaveborkedit/discord-ext-voice-recv)

## Project Status

Early version. Intended for experimentation and development. Breaking changes are expected.

## Features

* Connects to Discord voice channels
* Captures PCM audio from users
* Streams audio to an external server via WebSocket
* Receives and plays audio back in real time
* Automatic reconnection to the server

## Audio Specification

* Format: PCM 16-bit
* Discord input: 48 kHz stereo
* Server output: 24 kHz mono
* Transport: RTP over WebSocket

## Requirements

* Python 3.10+
* FFmpeg available in PATH
* Opus installed (required by Discord)

### Windows

* Microsoft Visual C++ Build Tools 14.x
* Microsoft Windows SDK

## Installation

Using a virtual environment is recommended.

```bash
python -m venv .venv
.\\.venv\\Scripts\\activate
pip install -r requirements.txt
```

## Configuration

Create the required config files:

* `config/api.py` → WebSocket server endpoint
* `config/__init__.py` → Discord token and channel IDs

## Usage

1. Start the bot
2. Invite it to a server with voice permissions
3. Use the commands:

   * `!join` → join the voice channel
   * `!leave` → leave the voice channel
   * `!jarvis <message>` → send text to the agent

## TODO / Roadmap

- Migrate to a single control connection to negotiate and manage audio WebSocket sessions.
- Add support for gRPC streaming, negotiated beforehand through the control channel.
- Improve protocol versioning and backward compatibility.
