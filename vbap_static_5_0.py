import numpy as np
import soundfile as sf
import vbap_implementation

def spatialize_audio_static(audio, source_angle_deg):


    gains, speaker_pair = vbap_implementation.vbap_2d_5_0(source_angle_deg)
    print(f"Gains applied: {np.round(gains, 3)} (from speakers {speaker_pair})")

    # Multiply mono audio by each gain
    spatialized = np.stack([audio * gain for gain in gains], axis=1)
    return spatialized

