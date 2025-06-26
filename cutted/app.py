import time
import threading
import customtkinter
from .core import gemini
from .core.logger import *
from .core import audio_processor
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import simpleaudio as sa  # Add this import

customtkinter.set_appearance_mode("Dark")

class CuttedApp:
    def __init__(self):
        self.AudioProcessor = audio_processor.AudioProcessor()
        self.gemini = gemini.GeminiClient()
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

        self.play_button = customtkinter.CTkButton(self.root, text="Play", command=self.play_audio, width=50)
        self.play_button.place(relx=0.3, rely=1.0, anchor="s", y=-30)
        self.stop_button = customtkinter.CTkButton(self.root, text="Stop", command=self.stop_audio, width=50)
        self.stop_button.place(relx=0.7, rely=1.0, anchor="s", y=-30)

        self.input_frame = customtkinter.CTkFrame(self.root, fg_color="transparent", height=36)
        self.input_frame.place(relx=0.5, rely=1.0, anchor="s", y=-90, relwidth=0.8)

        self.entry = customtkinter.CTkEntry(self.input_frame, height=32)
        self.entry.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.send_button = customtkinter.CTkButton(
            self.input_frame,
            text="➤",
            width=36,
            command=self.send_prompt
        )
        self.send_button.pack(side="right")
    
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
            
    def send_prompt(self):
        text = self.entry.get()
        print(f"Prompt: {text}")
        self.entry.delete(0, "end")
        
        gemini_result = self.gemini.generate(text)
        
        if gemini_result:
            print(gemini_result.name)
            args = gemini_result.args
            self.AudioProcessor.cut(args["start"][0], args["end"][0])
            self.update_plot()

    def run(self):
        self.root.mainloop()
        
def main():
    app = CuttedApp()
    app.run()