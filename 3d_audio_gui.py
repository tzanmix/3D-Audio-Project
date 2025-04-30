import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
import librosa
import tkinter as tk
from tkinter import filedialog, ttk
import scipy.io
import scipy.signal
import threading
import circular_space
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

# === PAN GAIN FOR LOUDSPEAKERS ===
def angle_diff(a, b):
    d = abs(a - b)
    return min(d, 360 - d)

def pan_gain(source_angle, speaker_angle):
    diff = angle_diff(source_angle, speaker_angle)
    return max(0, 1 - (diff / 90))

def normalize_gains(gains):
    total = np.sum(gains)
    return gains / total if total > 0 else gains


def process_audio(audio, sr, trajectory, dynamic, mode, source_angle_deg, output_file):
    
    if mode == "headphones":
        max_hrir_len = hrir_l.shape[2]
        out_len = len(audio) + max_hrir_len - 1
        out_l = np.zeros(out_len)
        out_r = np.zeros(out_len)

        for i, az in enumerate(trajectory):
            start, end = i * block_size, min((i + 1) * block_size, len(audio))
            block = audio[start:end]
            if len(block) < block_size:
                block = np.pad(block, (0, block_size - len(block)))
            az_idx = find_closest_azimuth(az)
            h_l = hrir_l[az_idx, cipic_elevation_index, :]
            h_r = hrir_r[az_idx, cipic_elevation_index, :]

            c_l = scipy.signal.fftconvolve(block, h_l)
            c_r = scipy.signal.fftconvolve(block, h_r)

            write_len = min(len(c_l), len(out_l) - start)
            out_l[start:start+write_len] += c_l[:write_len]
            out_r[start:start+write_len] += c_r[:write_len]

        output = np.stack([out_l, out_r], axis=1)
        output = output / np.max(np.abs(output))
    else:
        print("Processing 5.0 Surround Audio...")
        if dynamic:
            output = vbap_dynamic_5_0.spatialize_audio_dynamic(audio, sr)
        else:
            output = vbap_static_5_0.spatialize_audio_static(audio, source_angle_deg)

    sf.write(output_file, output, sample_rate)
    print(f"Audio saved: {output_file}")

# === GUI APPLICATION ===
class SpatialAudioApp:
    def __init__(self, root):
        self.root = root
        self.audio = None
        self.trajectory = []
        self.mode = tk.StringVar(value = "headphones")
        self.dynamic = tk.BooleanVar(value = True)
        self.fixed_azimuth = tk.DoubleVar(value = 0)

        self.build_gui()

    def build_gui(self):
        self.root.title("Spatial Audio Simulator")
        tk.Label(self.root, text="Select Audio File:").pack()
        tk.Button(self.root, text="Load Audio", command=self.load_audio).pack()

        tk.Label(self.root, text="Mode:").pack()
        ttk.Combobox(self.root, textvariable=self.mode, values=["headphones", "speakers"]).pack()

        tk.Label(self.root, text="Motion:").pack()
        ttk.Checkbutton(self.root, text="Dynamic", variable=self.dynamic).pack()
        
        tk.Label(self.root, text="Fixed Azimuth (if Static):").pack()

        self.fixed_azimuth = tk.DoubleVar(value=0)
        azimuth_selection = circular_space.PieChartApp(self.root, label_var=self.fixed_azimuth)
        tk.Label(self.root, textvariable=self.fixed_azimuth).pack()
        tk.Button(self.root, text="Run Simulation", command=self.run_simulation).pack()

    def load_audio(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav;*.mp3")])
        if file_path:
            self.audio, self.sr = librosa.load(file_path, sr=sample_rate, mono=True)
            self.audio = self.audio / np.max(np.abs(self.audio))  # Normalize
            print(f"Loaded: {file_path}")

    def generate_trajectory(self):
        num_blocks = int(np.ceil(len(self.audio) / block_size))
        if self.dynamic.get():
            speed_multiplier = 5  # Number of revolutions
            trajectory = np.linspace(0, 360 * speed_multiplier, num_blocks) % 360
            return trajectory
        return np.full(num_blocks, self.fixed_azimuth.get())

    def run_simulation(self):
        if self.audio is None:
            print("Load an audio file first!")
            return
        
        self.trajectory = self.generate_trajectory()
        threading.Thread(target=lambda: process_audio(self.audio, self.sr, self.trajectory, self.dynamic.get(), 
                        self.mode.get(), self.fixed_azimuth.get(), f"spatial_output{self.fixed_azimuth.get()}.wav")).start()
        # threading.Thread(target=lambda: process_audio(self.audio, self.sr, self.trajectory, self.mode.get(), f"spatial_output{self.fixed_azimuth.get()}.wav")).start()
        

# === RUN GUI ===
root = tk.Tk()
app = SpatialAudioApp(root)
root.mainloop()