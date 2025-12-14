import struct
from typing import Optional

class RTPPacket:
    """
    Clase para parsear y construir paquetes RTP (usados en Discord Voice para audio y video).
    """
    HEADER_SIZE = 12

    def __init__(self, 
                 version: int = 2, 
                 padding: int = 0, 
                 extension: int = 0, 
                 csrc_count: int = 0, 
                 marker: int = 0, 
                 payload_type: int = 0, 
                 sequence_number: int = 0, 
                 timestamp: int = 0, 
                 ssrc: int = 0, 
                 payload: bytes = b""):
        self.version = version
        self.padding = padding
        self.extension = extension
        self.csrc_count = csrc_count
        self.marker = marker
        self.payload_type = payload_type
        self.sequence_number = sequence_number
        self.timestamp = timestamp
        self.ssrc = ssrc
        self.payload = payload

    @classmethod
    def from_bytes(cls, data: bytes) -> "RTPPacket":
        """Convierte bytes en un objeto RTPPacket."""
        if len(data) < cls.HEADER_SIZE:
            raise ValueError("Paquete RTP demasiado corto")

        first_byte, second_byte, seq, ts, ssrc = struct.unpack("!BBHII", data[:cls.HEADER_SIZE])

        version = (first_byte >> 6) & 0x03
        padding = (first_byte >> 5) & 0x01
        extension = (first_byte >> 4) & 0x01
        csrc_count = first_byte & 0x0F

        marker = (second_byte >> 7) & 0x01
        payload_type = second_byte & 0x7F

        payload = data[cls.HEADER_SIZE:]

        return cls(version, padding, extension, csrc_count, marker,
                   payload_type, seq, ts, ssrc, payload)

    def to_bytes(self) -> bytes:
        """Convierte el objeto RTPPacket a bytes (listo para enviar)."""
        first_byte = (self.version << 6) | (self.padding << 5) | (self.extension << 4) | (self.csrc_count & 0x0F)
        second_byte = (self.marker << 7) | (self.payload_type & 0x7F)

        header = struct.pack("!BBHII", first_byte, second_byte,
                             self.sequence_number, self.timestamp, self.ssrc)

        return header + self.payload

    def is_audio(self) -> bool:
        """Heurística simple: Discord suele usar PT=120-127 para Opus."""
        return self.payload_type in range(120, 128)

    def is_video(self) -> bool:
        """Discord suele usar PT=96-127 para video (H.264, VP8)."""
        return self.payload_type in range(96, 120)
