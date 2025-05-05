import os
import numpy as np
import soundfile as sf
import librosa
import tkinter as tk
from tkinter import filedialog, ttk
import scipy.io
import threading
import circular_space
import dynamic_binaural
import static_binaural
import vbap_dynamic_5_0
import vbap_static_5_0

# === CONFIGURATION ===
cipic_file = "hrir_final.mat"
cipic_elevation_index = 9  # 0° elevation
cipic_azimuths = np.array([-180.0, -172.65306122, -165.30612245, -157.95918367, -150.6122449, -143.26530612, -135.91836735, -128.57142857, -121.2244898, -113.87755102, -106.53061224, -99.18367347, -91.83673469, -84.48979592, -77.14285714, -69.79591837, -62.44897959, -55.10204082, -47.75510204, -40.40816327, -33.06122449, -25.71428571, -18.36734694, -11.02040816, -3.67346939, 3.67346939, 11.02040816, 18.36734694, 25.71428571, 33.06122449, 40.40816327, 47.75510204, 55.10204082, 62.44897959, 69.79591837, 77.14285714, 84.48979592, 91.83673469, 99.18367347, 106.53061224, 113.87755102, 121.2244898, 128.57142857, 135.91836735, 143.26530612, 150.6122449, 157.95918367, 165.30612245, 172.65306122, 180.0
])

speakers = {'FL': -30, 'FR': 30, 'C': 0, 'SL': -110, 'SR': 110}
speaker_order = ['FL', 'FR', 'C', 'SL', 'SR']
block_size = 512
sample_rate = 44100

# === LOAD HRTF DATA ===
cipic_data = scipy.io.loadmat(cipic_file)
hrir_l = cipic_data['hrir_l']
hrir_r = cipic_data['hrir_r']

def find_closest_azimuth(deg):
    return np.argmin(np.abs(cipic_azimuths - deg))


def process_audio(audio, sr, dynamic, mode, source_angle_deg, output_file):
    if not os.path.exists(output_file):
        os.makedirs(output_file)
    if mode == "headphones":
        if dynamic:
            output = dynamic_binaural.spatialize_audio_dynamic(audio, sr)
        else:
            output = static_binaural.spatialize_audio_static(audio, sr, source_angle_deg)
    else:
        print("Processing 5.0 Surround Audio...")
        if dynamic:
            output = vbap_dynamic_5_0.spatialize_audio_dynamic(audio, sr)
        else:
            output = vbap_static_5_0.spatialize_audio_static(audio, source_angle_deg)

    if dynamic:
        output_file = output_file+"/spatial_output_dynamic.wav"
    else:
        output_file = output_file+f"/spatial_output{source_angle_deg}.wav"
    sf.write(output_file, output, sample_rate)
    print(f"Audio saved: {output_file}")

# === GUI APPLICATION ===
class SpatialAudioApp:
    def __init__(self, root):
        self.root = root
        self.audio = None
        self.mode = tk.StringVar(value = "headphones")
        self.dynamic = tk.BooleanVar(value = True)
        self.fixed_azimuth = tk.DoubleVar(value = 0)
        self.audio_file_loaded = tk.StringVar(value= "No audio file selected")

        self.build_gui()

    def build_gui(self):
        self.root.title("Spatial Audio Simulator")
        tk.Label(self.root, text="Select Audio File:").pack()
        tk.Button(self.root, text="Load Audio", command=self.load_audio).pack()
        tk.Label(self.root, textvariable=self.audio_file_loaded).pack()
        tk.Label(self.root, text="Mode:").pack()
        ttk.Combobox(self.root, textvariable=self.mode, values=["headphones", "speakers"]).pack()

        tk.Label(self.root, text="Motion:").pack()
        ttk.Checkbutton(self.root, text="Dynamic", variable=self.dynamic).pack()
        
        tk.Label(self.root, text="Fixed Azimuth (if Static):").pack()

        self.fixed_azimuth = tk.DoubleVar(value=0)
        circular_space.PieChartApp(self.root, label_var=self.fixed_azimuth)
        tk.Button(self.root, text="Run Simulation", command=self.run_simulation).pack()

    def load_audio(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav;*.mp3")])
        if file_path:
            self.audio, self.sr = librosa.load(file_path, sr=sample_rate, mono=True)
            self.audio = self.audio / np.max(np.abs(self.audio))  # Normalize
            print(f"Loaded: {file_path}")
            self.audio_file_loaded.set(file_path)

    def run_simulation(self):
        if self.audio is None:
            print("Load an audio file first!")
            return
        
        threading.Thread(target=lambda: process_audio(self.audio, self.sr, self.dynamic.get(), 
                        self.mode.get(), self.fixed_azimuth.get(), f"results_{self.mode.get()}")).start()
        

# === RUN GUI ===
root = tk.Tk()
app = SpatialAudioApp(root)
root.mainloop()