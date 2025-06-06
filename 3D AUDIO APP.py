import os
import numpy as np
import soundfile as sf
import librosa
import customtkinter as tk
from tkinter import filedialog
import threading
import azimuth_canvas
import dynamic_binaural
import static_binaural
import vbap_dynamic_5_0
import vbap_static_5_0
import pygame
import os

block_size = 512
sample_rate = 44100
pygame.mixer.init()
base_path = os.path.dirname(__file__)


class Splash(tk.CTkToplevel):
    def __init__(self, parent, mode, dynamic):
        self.mode = mode
        self.dynamic = dynamic
        tk.CTkToplevel.__init__(self, parent)
        self.title("")
        self.geometry("300x100")
        if self.dynamic:
            self.dynamic = "dynamic"
        else:
            self.dynamic = "static"
        tk.CTkLabel(self, text="Processing "+self.dynamic +" audio for "+self.mode+"...").pack()
        self.grab_set()




class SpatialAudioApp:
    def __init__(self, root):
        self.root = root
        self.audio = None
        self.mode = tk.StringVar(value = "headphones")
        self.play_button_symbol = tk.StringVar(value= "▶")
        self.dynamic = tk.BooleanVar(value = False)
        self.fixed_azimuth = tk.DoubleVar(value = 0)
        self.audio_file_loaded = tk.StringVar(value= "No audio file selected")
        self.isPlaying = False
        self.paused_input = False
        self.track_length = 0
        self.playing_output = False
        self.paused_output = False
        self.output_mixer_button_text = tk.StringVar(value="Play Output")
        self.out_file = ''
        self.build_gui()
        

    def build_gui(self):
        self.root.title("Spatial Audio Simulator")
        self.root.geometry("400x650")
        tk.CTkLabel(self.root, text="Select Audio File:").pack()
        tk.CTkButton(self.root, text="Load Audio", command=self.load_audio).pack()
        tk.CTkLabel(self.root, textvariable=self.audio_file_loaded).pack()
        tk.CTkButton(self.root, textvariable=self.play_button_symbol, command=self.play_audio).pack()
        tk.CTkLabel(self.root, text="Mode:").pack()
        tk.CTkComboBox(self.root, variable=self.mode, values=["headphones", "speakers"]).pack()
        tk.CTkLabel(self.root, text="Motion:").pack()
        tk.CTkRadioButton(self.root, text="Static", variable=self.dynamic, value=False).pack()
        tk.CTkRadioButton(self.root, text="Dynamic", variable=self.dynamic, value=True).pack()        
        tk.CTkLabel(self.root, text="Fixed Azimuth (if Static):").pack()
        self.fixed_azimuth = tk.DoubleVar(value=0)
        azimuth_canvas.AzimuthSelectionApp(self.root, label_var=self.fixed_azimuth)
        tk.CTkButton(self.root, text="Process Audio", command=self.run_simulation).pack(pady=5)
        tk.CTkButton(self.root, textvariable=self.output_mixer_button_text, command=self.play_output).pack(pady=5)
    
    

    def load_audio(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav;*.mp3")])
        pygame.mixer.music.unload()
        if file_path:
            self.audio, self.sr = librosa.load(file_path, sr=sample_rate, mono=True)
            self.audio = self.audio / np.max(np.abs(self.audio))
            print(f"Loaded: {os.path.basename(file_path)[:-4]}")
            self.audio_file_loaded.set(os.path.basename(file_path)[:-4])
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            pygame.mixer.music.pause()
            self.track_length = int(pygame.mixer.Sound(file_path).get_length())
    
    def play_audio(self):
        if self.isPlaying:
            pygame.mixer.music.pause()
            self.play_button_symbol.set("▶")
        else:
            pygame.mixer.music.unpause()
            self.play_button_symbol.set("⏸")
        self.isPlaying = not self.isPlaying
        print(self.isPlaying)
        print("Now playing")
        

    def run_simulation(self):
        if self.audio is None:
            print("Load an audio file first!")
            return
        global splash
        splash = Splash(self.root, self.mode.get(), self.dynamic.get())
        self.paused_output = False
        self.playing_output = False
        threading.Thread(target=lambda: self.process_audio(self.audio, self.sr, self.dynamic.get(), 
                        self.mode.get(), self.fixed_azimuth.get(), f"results_{self.mode.get()}")).start()
    
    
    def play_output(self):
        if self.audio is None:
            print("Load an audio file first!")
            return
        if not self.playing_output and not self.paused_output:
            print("Now playing: ", self.out_file)
            self.paused_output = False
            self.output_mixer_button_text.set("Pause Output")
            pygame.mixer.music.pause()
            pygame.mixer.music.unload()
            pygame.mixer.music.load(self.out_file)
            pygame.mixer.music.play()
        elif self.playing_output and not self.paused_output:
            self.paused_output = True
            self.output_mixer_button_text.set("Play Output")
            pygame.mixer.music.pause()
        else:
            self.paused_output = False
            self.output_mixer_button_text.set("Pause Output")
            pygame.mixer.music.unpause()
        self.playing_output = not self.playing_output

    def process_audio(self, audio, sr, dynamic, mode, source_angle_deg, output_file):
        output_file = os.path.join(base_path, output_file)
        if not os.path.exists(output_file):
            os.makedirs(output_file)
        if mode == "headphones":
            if dynamic:
                output = dynamic_binaural.spatialize_audio_dynamic(audio, sr)
            else:
                output = static_binaural.spatialize_audio_static(audio, source_angle_deg)
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
        self.out_file = output_file
        splash.destroy()
        

root = tk.CTk()
app = SpatialAudioApp(root)
root.mainloop()
