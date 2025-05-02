import numpy as np
import scipy.io
import scipy.signal
from scipy.signal import butter, sosfilt, minimum_phase

# === Config ===
hrir_path = "hrir_final.mat"
target_elevation = 9
    
# === Load CIPIC HRIR data ===
cipic = scipy.io.loadmat(hrir_path)
hrir_l_raw = cipic['hrir_l']  # shape: (25, 50, 200)
hrir_r_raw = cipic['hrir_r']

# === CIPIC standard azimuths and elevations ===
elevations = np.linspace(-45, 230.625, 25)
azimuths = np.array([-180.0, -172.65306122, -165.30612245, -157.95918367, -150.6122449, -143.26530612, -135.91836735, -128.57142857, -121.2244898, -113.87755102, -106.53061224, -99.18367347, -91.83673469, -84.48979592, -77.14285714, -69.79591837, -62.44897959, -55.10204082, -47.75510204, -40.40816327, -33.06122449, -25.71428571, -18.36734694, -11.02040816, -3.67346939, 3.67346939, 11.02040816, 18.36734694, 25.71428571, 33.06122449, 40.40816327, 47.75510204, 55.10204082, 62.44897959, 69.79591837, 77.14285714, 84.48979592, 91.83673469, 99.18367347, 106.53061224, 113.87755102, 121.2244898, 128.57142857, 135.91836735, 143.26530612, 150.6122449, 157.95918367, 165.30612245, 172.65306122, 180.0
])

def get_nearest_hrir_indices(target_az, target_el):
    el_idx = (np.abs(elevations - target_el)).argmin()
    az_idx = (np.abs(azimuths - target_az)).argmin()
    return el_idx, az_idx

# === Zero-pad HRIRs to 256 samples ===
def pad_hrir(hrir, target_len=256):
    return np.pad(hrir, (0, max(0, target_len - len(hrir))), mode='constant')

# === Optional: high-pass filter to reduce low-end rumble ===
def highpass(signal, sr, cutoff=80, order=4):
    sos = butter(order, cutoff, btype='highpass', fs=sr, output='sos')
    return sosfilt(sos, signal)

def spatialize_audio_static(audio, sr, target_azimuth):

    # === Select nearest HRIR ===
    el_idx, az_idx = get_nearest_hrir_indices(target_azimuth, target_elevation)
    hrir_l = hrir_l_raw[el_idx, az_idx, :]
    hrir_r = hrir_r_raw[el_idx, az_idx, :]
    print(f"Using HRTF for azimuth {azimuths[az_idx]}°, elevation {elevations[el_idx]}°")


    hrir_l = pad_hrir(hrir_l)
    hrir_r = pad_hrir(hrir_r)

    # === Convolution ===
    left = scipy.signal.fftconvolve(audio, hrir_l, mode='full')
    right = scipy.signal.fftconvolve(audio, hrir_r, mode='full')

    left = highpass(left, sr)
    right = highpass(right, sr)

    # === Trim to equal length and normalize with headroom ===
    min_len = min(len(left), len(right))
    left = left[:min_len]
    right = right[:min_len]

    max_val = max(np.max(np.abs(left)), np.max(np.abs(right)))
    headroom_db = -3
    scaling = 10**(headroom_db / 20)
    left *= scaling / max_val
    right *= scaling / max_val

    # === Combine to stereo and save ===
    stereo = np.stack([left, right], axis=1)

    return stereo
