from pydub import *
from pydub.utils import ratio_to_db
from .logger import *
import numpy as np
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure

class AudioProcessor:
    def __init__(self):
        self.audio_path = None
    
    def load_audio(self, audio_path: str, volume: float = 1.0):
        self.audio_path = audio_path
        self.audio = AudioSegment.from_file(self.audio_path)
        self.audio = self.audio.apply_gain(ratio_to_db(volume))
        print_info(f"Loaded {self.audio_path}")
        
    def plot_audio(self, save_path=None):
        if self.audio is None:
            print_fail("No audio loaded.")
            return
        
        samples = np.array(self.audio.get_array_of_samples())
        if self.audio.channels == 2:
            samples = samples.reshape((-1, 2))
            samples = samples.mean(axis=1)
                
        times = np.linspace(0, len(samples) / self.audio.frame_rate, num=len(samples))
        
        fig = Figure(figsize=(5, 4))
        ax = fig.add_subplot()
        line, = ax.plot(times, samples)
        
        # remove text
        ax.set_title("")
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_yticks([])
        
        return fig
    
    def get_lenght(self):
        self.duration = self.audio.duration_seconds
        self.duration = round(self.duration, 2)
        return self.duration