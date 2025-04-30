import numpy as np

def normalize(v):
    """Normalize a 2D vector."""
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm

def vbap_2d(source_angle_deg, speaker_angles_deg):
    """
    Calculate gain coefficients for 2D VBAP.

    Parameters:
    - source_angle_deg: angle of source in degrees (0° is in front, positive is counter-clockwise)
    - speaker_angles_deg: list of two speaker angles in degrees (assumes pairwise setup)

    Returns:
    - gains: numpy array of gain coefficients [g1, g2] for each speaker
    """
    # Convert angles to radians
    source_angle_rad = np.radians(source_angle_deg)
    speaker_angles_rad = np.radians(speaker_angles_deg)

    # Unit vectors for speakers
    l1 = np.array([np.cos(speaker_angles_rad[0]), np.sin(speaker_angles_rad[0])])
    l2 = np.array([np.cos(speaker_angles_rad[1]), np.sin(speaker_angles_rad[1])])

    # Speaker matrix
    L = np.column_stack((l1, l2))

    # Invert speaker matrix
    try:
        L_inv = np.linalg.inv(L)
    except np.linalg.LinAlgError:
        raise ValueError("Speaker vectors must not be collinear")

    # Source direction vector
    source_vec = np.array([np.cos(source_angle_rad), np.sin(source_angle_rad)])

    # Gains (un-normalized)
    gains = np.dot(L_inv, source_vec)

    # Zero negative gains (outside triangle)
    gains[gains < 0] = 0

    # Normalize gains to unit power
    gains = normalize(gains)

    return gains

# Example usage:
speaker_angles = [-30, 30]  # Two speakers at -30° and +30°
source_angle = 10           # Source is at 10°
gains = vbap_2d(source_angle, speaker_angles)

print(f"Gains for speakers at {speaker_angles}° with source at {source_angle}°: {gains}")
