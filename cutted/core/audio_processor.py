from pydub import *
from pydub.utils import ratio_to_db
from .logger import *
import numpy as np
from matplotlib.figure import Figure

class AudioProcessor:
    def __init__(self):
        self.audio_path = None
    
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