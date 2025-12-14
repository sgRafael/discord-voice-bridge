import numpy as np
import struct

def detectar_canales(pcm_bytes):
    # 16-bit PCM, 48 kHz, frame típico de 20 ms
    if len(pcm_bytes) == 1920:
        return 1
    if len(pcm_bytes) == 3840:
        return 2
    return None

def stereo_to_mono(x: np.ndarray) -> np.ndarray:
    # x shape: (2*n,), int16 interleaved LR
    stereo = x.reshape(-1, 2)
    return stereo.astype(np.int32).mean(axis=1).astype(np.int16)

def mono_to_stereo(mono: np.ndarray) -> np.ndarray:
    return np.repeat(mono[:, None], 2, axis=1).astype(np.int16)



