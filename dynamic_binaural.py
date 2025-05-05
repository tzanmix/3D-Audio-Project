import numpy as np
import scipy.io
import scipy.signal
from scipy.signal import butter, sosfilt, minimum_phase
import pysofaconventions as sofa

# === Config ===
sofa_file_path = "D2_96K_24bit_512tap_FIR_SOFA.sofa"
frame_size = 2048
hop_size = 1024  # 50% overlap
hrir_pad_len = 256
elevation = 0  # fixed elevation

# === Load SOFA HRIRs ===
sf_obj = sofa.SOFAFile(sofa_file_path, 'r')
hrirs = sf_obj.getDataIR()  # shape: [M, 2, N]
positions = sf_obj.getVariableValue("SourcePosition")  # shape: [M, 3] (azimuth, elev, distance)

# === Find closest match ===
def find_nearest_hrir(target_az, target_el, positions):
    diffs = positions[:, :2] - np.array([target_az, target_el])
    dists = np.linalg.norm(diffs, axis=1)
    return np.argmin(dists)

def pad_hrir(hrir, target_len=256):
    return np.pad(hrir, (0, max(0, target_len - len(hrir))), mode='constant')

def highpass(signal, sr, cutoff=80, order=4):
    sos = butter(order, cutoff, btype='highpass', fs=sr, output='sos')
    return sosfilt(sos, signal)

def spatialize_audio_dynamic(audio, sr):
    # === Set up output buffer ===
    n_frames = int(np.ceil((len(audio) - frame_size) / hop_size)) + 1
    output_len = (n_frames - 1) * hop_size + frame_size + hrir_pad_len - 1
    output_left = np.zeros(output_len)
    output_right = np.zeros(output_len)


    # === Process audio frame by frame ===
    for i in range(n_frames):
        start = i * hop_size
        end = start + frame_size
        frame = audio[start:end]
        if len(frame) < frame_size:
            frame = np.pad(frame, (0, frame_size - len(frame)))

        # Dynamic azimuth from -180° to +180°
        sweep_cycles = n_frames // 5
        frame_in_sweep = i  % sweep_cycles
        azimuth = 0 + 360 * (frame_in_sweep / sweep_cycles)
        idx = find_nearest_hrir(azimuth, elevation, positions)

        # Get HRIRs, convert to min-phase, and pad
        hrir_l = pad_hrir(hrirs[idx, 0, :], hrir_pad_len)
        hrir_r = pad_hrir(hrirs[idx, 1, :], hrir_pad_len)

        # Convolve
        conv_l = scipy.signal.fftconvolve(frame, hrir_l, mode='full')
        conv_r = scipy.signal.fftconvolve(frame, hrir_r, mode='full')

        # High-pass to remove low-end artifacts
        conv_l = highpass(conv_l, sr)
        conv_r = highpass(conv_r, sr)

        out_start = start
        out_end = start + len(conv_l)

        if out_end > output_len:
            conv_l = conv_l[:output_len - out_start]
            conv_r = conv_r[:output_len - out_start]
            out_end = output_len

        output_left[out_start:out_end] += conv_l
        output_right[out_start:out_end] += conv_r

    # === Normalize output with -3 dB headroom ===
    max_val = max(np.max(np.abs(output_left)), np.max(np.abs(output_right)))
    scaling = 10 ** (-3 / 20) / max_val
    output_left *= scaling
    output_right *= scaling

    stereo = np.stack([output_left, output_right], axis=1)
    return stereo


