import numpy as np
import scipy.signal
import pysofaconventions as sofa
import os


# Config with SOFA db
target_elevation = 9

base_path = os.path.dirname(__file__)
sofa_file_path = os.path.join(base_path, "D2_96K_24bit_512tap_FIR_SOFA.sofa")
sf_obj = sofa.SOFAFile(sofa_file_path, 'r')
hrirs = sf_obj.getDataIR()
positions = sf_obj.getVariableValue("SourcePosition")

# Find closest match
def find_nearest_hrir(target_az, target_el, positions):
    diffs = positions[:, :2] - np.array([target_az, target_el])
    dists = np.linalg.norm(diffs, axis=1)
    return np.argmin(dists)

def spatialize_audio_static(audio, selected_azimuth):
    # gui azimuth selection ranges from -180 to 180 degrees
    # while sofa available azimuths from 0 to 360 degrees
    if selected_azimuth == -180:
        target_azimuth = 180
    elif selected_azimuth == 0:
        target_azimuth = -180
    else:
        target_azimuth = selected_azimuth + 180
    print(f"Selected Azimuth: {selected_azimuth},  Target Azimuth: {target_azimuth}")
    # Select nearest HRIR
    idx = find_nearest_hrir(target_azimuth, target_elevation, positions)
    hrir_l = hrirs[idx, 0, :]
    hrir_r = hrirs[idx, 1, :]
    print(f"Using HRIR #{idx} for azimuth={positions[idx, 0]}°, elevation={positions[idx, 1]}°")

    # Convolve audio
    left = scipy.signal.fftconvolve(audio, hrir_l, mode='full')
    right = scipy.signal.fftconvolve(audio, hrir_r, mode='full')

    # Normalize and trim
    min_len = min(len(left), len(right))
    left = left[:min_len]
    right = right[:min_len]

    max_val = max(np.max(np.abs(left)), np.max(np.abs(right)))
    if max_val > 0:
        scale = 0.99 / max_val
        left *= scale
        right *= scale

    # Combine stereo
    stereo = np.stack([left, right], axis=1)

    return stereo


