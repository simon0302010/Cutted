import time
import threading
import customtkinter
from .core.logger import *
from .core import audio_processor

from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure

import simpleaudio as sa  # Add this import

customtkinter.set_appearance_mode("Dark")

class CuttedApp:
    def __init__(self):
        self.AudioProcessor = audio_processor.AudioProcessor()
        self.canvas = None
        self.cursor_line = None
        self.last_slider_update = 0
        self.play_obj = None
        self.play_thread = None
        self.is_playing = False
        self.setup_ui()
    
    def setup_ui(self):
        self.root = customtkinter.CTk()
        self.root.title("Cutted")
        self.root.geometry("600x400")
        
        self.root.bind("<Configure>", self.on_resize)
        
        self.plot_frame = customtkinter.CTkFrame(self.root, height=250, fg_color="transparent")
        self.plot_frame.pack(
            side=customtkinter.TOP, 
            fill=customtkinter.BOTH, 
            expand=True, 
            padx=20,
            pady=(20, 150),
        )
        self.plot_frame.pack_propagate(False)
        
        button = customtkinter.CTkButton(self.root, text="Load audio", command=self.select_file)
        button.place(relx=0.5, rely=1.0, anchor="s", y=-30)

        self.textbox = customtkinter.CTkTextbox(self.root, height=10)
        self.textbox.place(relx=0.5, rely=1.0, anchor="center", relwidth=0.8, y=-90)

        self.play_button = customtkinter.CTkButton(self.root, text="Play", command=self.play_audio, width=50)
        self.play_button.place(relx=0.3, rely=1.0, anchor="s", y=-30)
        self.stop_button = customtkinter.CTkButton(self.root, text="Stop", command=self.stop_audio, width=50)
        self.stop_button.place(relx=0.7, rely=1.0, anchor="s", y=-30)
    
    def on_resize(self, event):
        if hasattr(self, "slider") and self.slider is not None:
            new_width = max(self.root.winfo_width() - 40, 100)
            self.slider.configure(width=new_width)
    
    def select_file(self):
        file_path = customtkinter.filedialog.askopenfilename(
            filetypes=[("Audio files", ".mp3 .wav .aac .flac .ogg .m4a")]
        )
        if file_path:
            self.AudioProcessor.load_audio(file_path)
            self.update_plot()

    def update_plot(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        
        fig = self.AudioProcessor.plot_audio()
        self.ax = fig.axes[0]
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        
        self.audio_lenght = int(round(self.AudioProcessor.get_lenght()))
        
        slider_width = self.root.winfo_width() - 40
        self.slider = customtkinter.CTkSlider(
            self.root, from_=0, to=self.audio_lenght, command=self.set_cursor, width=slider_width
        )
        self.slider.set(0)
        
        self.slider.place(relx=0.5, rely=1.0, anchor="s", y=-130)
        
        self.canvas.get_tk_widget().pack(
            fill=customtkinter.BOTH, 
            expand=True, 
            padx=10,
            pady=10,
        )
        
        self.cursor_line = self.ax.axvline(x=0, color="red", linewidth=2)
        self.canvas.draw_idle()
        
    def set_cursor(self, value):
        now = time.time()
        if now - self.last_slider_update < 0.1:  # 100ms
            return
        self.last_slider_update = now
        
        self.slider_value = round(value)
        
        if self.cursor_line:
            self.cursor_line.set_xdata([self.slider_value, self.slider_value])
            self.canvas.draw_idle()
        
        print(f"Slider Value: {self.slider_value}")

    def play_audio(self):
        if not hasattr(self.AudioProcessor, "audio") or self.AudioProcessor.audio is None:
            print_fail("No audio loaded.")
            return

        self.stop_audio()

        start_ms = int(self.slider.get() * 1000)
        audio = self.AudioProcessor.audio[start_ms:]
        raw_data = audio.raw_data
        num_channels = audio.channels
        bytes_per_sample = audio.sample_width
        sample_rate = audio.frame_rate

        def playback():
            self.is_playing = True
            self.play_obj = sa.play_buffer(raw_data, num_channels, bytes_per_sample, sample_rate)
            self.play_obj.wait_done()
            self.is_playing = False

        self.play_thread = threading.Thread(target=playback, daemon=True)
        self.play_thread.start()

    def stop_audio(self):
        if self.play_obj is not None and self.is_playing:
            self.play_obj.stop()
            self.is_playing = False

    def run(self):
        self.root.mainloop()
        
def main():
    app = CuttedApp()
    app.run()