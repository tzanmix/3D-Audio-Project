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

        t = start / sr  # Time in seconds
        angle = angle_function(t)

        gains, _ = vbap_implementation.vbap_2d_5_0(angle)

        for ch in range(5):
            output_audio[start:end, ch] = block * gains[ch]

    return output_audio

# Example usage: pan from left to right across 5 seconds
def angle_function(t):
    return -180 + 360 * (t / 10.0)  # sweep -90° to +90° over 10 seconds

