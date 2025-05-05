import numpy as np


def normalize(v):
    """Normalize a vector to unit power."""
    norm = np.linalg.norm(v)
    return v / norm if norm > 0 else v

def vbap_2d_5_0(source_angle_deg):
    # Speaker setup: angles in degrees, order matters
    speaker_angles = [-30, 30, 0, -110, 110]
    speaker_names = ["FL", "FR", "C", "SL", "SR"]

    # Define all valid speaker pairs for VBAP
    speaker_pairs = [
        (0, 2),  # FL - C
        (2, 1),  # C - FR
        # (0, 1),  # FL - FR
        (0, 3),  # FL - SL
        (1, 4),  # FR - SR
        (3, 4),  # SL - SR
    ]

    source_angle_rad = np.radians(source_angle_deg)
    source_vec = np.array([np.cos(source_angle_rad), np.sin(source_angle_rad)])

    best_gains = None
    best_pair = None

    for i, j in speaker_pairs:
        # Create matrix from the two speaker direction vectors
        v1 = np.array([np.cos(np.radians(speaker_angles[i])), np.sin(np.radians(speaker_angles[i]))])
        v2 = np.array([np.cos(np.radians(speaker_angles[j])), np.sin(np.radians(speaker_angles[j]))])
        L = np.column_stack((v1, v2))

        try:
            L_inv = np.linalg.inv(L)
        except np.linalg.LinAlgError:
            continue  # Skip collinear or invalid pairs

        gains_pair = np.dot(L_inv, source_vec)

        if np.all(gains_pair >= 0):  # Valid pair found
            gains_pair = normalize(gains_pair)
            gains_full = np.zeros(len(speaker_angles))
            gains_full[i] = gains_pair[0]
            gains_full[j] = gains_pair[1]
            best_gains = gains_full
            best_pair = (speaker_names[i], speaker_names[j])
            break

    if best_gains is None:
        raise ValueError("No suitable speaker pair found for the given source direction")

    return best_gains, best_pair
