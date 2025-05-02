import numpy as np
import scipy.io
import scipy.signal
from scipy.signal import butter, sosfilt, minimum_phase

# === Config ===
hrir_path = "hrir_final.mat"
frame_size = 2048
hop_size = 1024  # 50% overlap
hrir_pad_len = 256
elevation = 0  # fixed elevation

# === Load CIPIC HRIRs ===
cipic = scipy.io.loadmat(hrir_path)
hrir_l_raw = cipic['hrir_l']
hrir_r_raw = cipic['hrir_r']

elevations = np.linspace(-45, 230.625, 25)
azimuths = np.array([-180.0, -172.65306122, -165.30612245, -157.95918367, -150.6122449, -143.26530612, -135.91836735, -128.57142857, -121.2244898, -113.87755102, -106.53061224, -99.18367347, -91.83673469, -84.48979592, -77.14285714, -69.79591837, -62.44897959, -55.10204082, -47.75510204, -40.40816327, -33.06122449, -25.71428571, -18.36734694, -11.02040816, -3.67346939, 3.67346939, 11.02040816, 18.36734694, 25.71428571, 33.06122449, 40.40816327, 47.75510204, 55.10204082, 62.44897959, 69.79591837, 77.14285714, 84.48979592, 91.83673469, 99.18367347, 106.53061224, 113.87755102, 121.2244898, 128.57142857, 135.91836735, 143.26530612, 150.6122449, 157.95918367, 165.30612245, 172.65306122, 180.0
])
# azimuths = np.concatenate([azimuths, 180 - azimuths[::-1]])[:50]

def get_nearest_hrir_indices(target_az, target_el):
    el_idx = (np.abs(elevations - target_el)).argmin()
    az_idx = (np.abs(azimuths - target_az)).argmin()
    return el_idx, az_idx

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

        # Dynamic azimuth from -80° to +80°
        azimuth = -180 + (360 * i / max(1, n_frames - 1))
        el_idx, az_idx = get_nearest_hrir_indices(azimuth, elevation)

        # Get HRIRs, convert to min-phase, and pad
        hrir_l = minimum_phase(pad_hrir(hrir_l_raw[el_idx, az_idx, :], hrir_pad_len))
        hrir_r = minimum_phase(pad_hrir(hrir_r_raw[el_idx, az_idx, :], hrir_pad_len))

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


