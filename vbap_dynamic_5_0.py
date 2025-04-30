import numpy as np
import soundfile as sf

def normalize(v):
    norm = np.linalg.norm(v)
    return v / norm if norm > 0 else v

def vbap_2d_5_0(source_angle_deg):
    speaker_angles = [-30, 0, 30, -110, 110]
    speaker_pairs = [
        (0, 1),  # FL - C
        (1, 2),  # C - FR
        (0, 2),  # FL - FR
        (0, 3),  # FL - SL
        (2, 4),  # FR - SR
        (3, 4),  # SL - SR
    ]

    source_angle_rad = np.radians(source_angle_deg)
    source_vec = np.array([np.cos(source_angle_rad), np.sin(source_angle_rad)])

    for i, j in speaker_pairs:
        v1 = np.array([np.cos(np.radians(speaker_angles[i])), np.sin(np.radians(speaker_angles[i]))])
        v2 = np.array([np.cos(np.radians(speaker_angles[j])), np.sin(np.radians(speaker_angles[j]))])
        L = np.column_stack((v1, v2))

        try:
            L_inv = np.linalg.inv(L)
        except np.linalg.LinAlgError:
            continue

        gains_pair = np.dot(L_inv, source_vec)
        if np.all(gains_pair >= 0):
            gains_pair = normalize(gains_pair)
            gains_full = np.zeros(5)
            gains_full[i] = gains_pair[0]
            gains_full[j] = gains_pair[1]
            return gains_full, (i, j)

    raise ValueError("No valid speaker pair found.")

def spatialize_audio_dynamic(input_path, output_path, angle_func, block_size=1024):
    mono_audio, sr = sf.read(input_path)
    if mono_audio.ndim > 1:
        raise ValueError("Input must be mono.")

    n_samples = len(mono_audio)
    n_blocks = int(np.ceil(n_samples / block_size))

    output_audio = np.zeros((n_samples, 5))

    for block_idx in range(n_blocks):
        start = block_idx * block_size
        end = min((block_idx + 1) * block_size, n_samples)
        block = mono_audio[start:end]

        t = start / sr  # Time in seconds
        angle = angle_func(t)

        gains, _ = vbap_2d_5_0(angle)

        for ch in range(5):
            output_audio[start:end, ch] = block * gains[ch]

    sf.write(output_path, output_audio, sr)
    print(f"Dynamic spatialized audio written to: {output_path}")

# Example usage: pan from left to right across 5 seconds
def angle_function(t):
    return -90 + 180 * (t / 5.0)  # sweep -90° to +90° over 5 seconds

spatialize_audio_dynamic(
    input_path="project_audio.wav",
    output_path="vbap_dynamic_5_0.wav",
    angle_func=angle_function,
    block_size=1024
)
