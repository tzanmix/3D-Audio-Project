import numpy as np
import soundfile as sf
import vbap_implementation

def spatialize_audio_dynamic(audio, sr, block_size=1024):
    

    n_samples = len(audio)
    n_blocks = int(np.ceil(n_samples / block_size))

    output_audio = np.zeros((n_samples, 5))

    for block_idx in range(n_blocks):
        start = block_idx * block_size
        end = min((block_idx + 1) * block_size, n_samples)
        block = audio[start:end]

        t = start / sr
        angle = angle_function(t)

        gains, _ = vbap_implementation.vbap_2d_5_0(angle)

        for ch in range(5):
            output_audio[start:end, ch] = block * gains[ch]

    return output_audio

# pan from left to right - 30 seconds for the full motion
def angle_function(t):
    return -180 + 360 * (t / 30.0)

