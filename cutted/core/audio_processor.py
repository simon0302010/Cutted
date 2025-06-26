from pydub import *
from pydub.utils import ratio_to_db
from .logger import *
import numpy as np
from matplotlib.figure import Figure
import pygame
import io
import threading
import time

class AudioProcessor:
    def __init__(self):
        self.audio_path = None
        self.audio = None
        self.is_playing = False
        self.play_thread = None
        self._init_pygame()
    
    def _init_pygame(self):
        try:
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
            pygame.mixer.init()
            print_success("Pygame initialized")
        except pygame.error as e:
            print_warn(f"Pygame initialization warning: {e}")
    
    def load_audio(self, audio_path: str, volume: float = 1.0):
        self.audio_path = audio_path
        self.audio = AudioSegment.from_file(self.audio_path)
        self.audio = self.audio.apply_gain(ratio_to_db(volume))
        print_info(f"Loaded {self.audio_path}")
        
    def plot_audio(self):
        if self.audio is None:
            print_fail("No audio loaded.")
            return
        
        samples = np.array(self.audio.get_array_of_samples())
        if self.audio.channels == 2:
            samples = samples.reshape((-1, 2))
            samples = samples.mean(axis=1)
        
        samples = samples / np.max(np.abs(samples))
        
        times = np.linspace(0, len(samples) / self.audio.frame_rate, num=len(samples))
        print(times)
        
        fig = Figure(figsize=(5, 4), facecolor="#242424")
        ax = fig.add_subplot()
        ax.set_facecolor("#242424")
        line, = ax.plot(times, samples, color="cyan", linewidth=1.5)
        
        # remove text
        ax.set_title("")
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_yticks([])
        
        ax.margins(0)
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        
        ax.set_xlim(times[0], times[-1])
        ax.set_ylim(np.min(samples), np.max(samples))
        
        return fig
    
    def get_lenght(self):
        self.duration = self.audio.duration_seconds
        self.duration = round(self.duration, 2)
        return self.duration
    
    def cut(self, start, end):
        if type(start) == list and type(end) == list:
            print("Cutting multiple segments")
        
        start_ms = round(start * 1000)
        end_ms = round(end * 1000)
        
        self.audio = self.audio[:start_ms] + self.audio[end_ms:]
        
    def play_audio(self, start_time=0):
        if self.audio is None:
            print_fail("No audio loaded.")
            return False
        
        try:
            self.stop_audio()
            
            start_ms = int(start_time * 1000)
            audio_segment = self.audio[start_ms:]
            
            audio_segment = audio_segment.set_frame_rate(22050)
            audio_segment = audio_segment.set_channels(2)
            audio_segment = audio_segment.set_sample_width(2)
            
            audio_data = io.BytesIO()
            audio_segment.export(audio_data, format="wav")
            audio_data.seek(0)
            
            pygame.mixer.music.load(audio_data)
            pygame.mixer.music.play()
            self.is_playing = True
            
            print_success(f"Playing audio from {start_time}s")
            return True
        
        except Exception as e:
            print_fail(f"Error playing audio: {e}")
            return False
        
    def stop_audio(self):
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                self.is_playing = False
                print_info("Audio playback stopped")
        except Exception as e:
            print_warn(f"Error stopping audio: {e}")
            
    def is_playing(self):
        try:
            if pygame.mixer.get_init():
                return pygame.mixer.music.get_busy()
            return False
        except:
            return False
        
    def get_audio_info(self):
        if self.audio is None:
            return None
        
        return {
            "duration": self.get_lenght(),
            "channels": self.audio.channels,
            "frame_rate": self.audio.frame_rate,
            "sample_width": self.audio.sample_width
        }