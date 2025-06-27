import time
import customtkinter
import tkinter.messagebox as messagebox
from .core import gemini
from .core.logger import *
from .core import audio_processor
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

customtkinter.set_appearance_mode("Dark")

try:
    from .core import transcribe
    whisper_support = True
    print_info("Whisper support present.")
except:
    whisper_support = False
    print_info("Whisper support is not present.")

class CuttedApp:
    def __init__(self):
        self.AudioProcessor = audio_processor.AudioProcessor()
        if whisper_support:
            self.whisper = None
        self.gemini = gemini.GeminiClient()
        self.canvas = None
        self.cursor_line = None
        self.last_slider_update = 0
        self.is_playing = False
        self.last_states = []
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
        
        export_button = customtkinter.CTkButton(self.root, text="Export", command=self.export_audio, width=70)
        export_button.place(relx=0.9, rely=1.0, anchor="s", y=-30)
        
        undo_button = customtkinter.CTkButton(self.root, text="Undo", command=self.undo_last, width=70)
        undo_button.place(relx=0.1, rely=1.0, anchor="s", y=-30)
        
        if whisper_support:
            self.use_transcript_checkbox = customtkinter.CTkCheckBox(
                self.root,
                text="Give Gemini a transcript (very slow)",
                text_color="#888888",
                font=("Arial", 12)
            )
            self.use_transcript_checkbox.place(relx=0.0, rely=1.0, anchor="w", y=-12)

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

        start_time = self.slider.get() if hasattr(self, 'slider') else 0
        self.AudioProcessor.play_audio(start_time)

    def stop_audio(self):
        self.AudioProcessor.stop_audio()
        self.is_playing = False
        
    def export_audio(self):
        if not hasattr(self.AudioProcessor, "audio") or self.AudioProcessor.audio is None:
            print_fail("No audio loaded.")
            return
        
        save_path = customtkinter.filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[
                ("MP3 files", "*.mp3"),
                ("WAV files", "*.wav"),
            ]
        )
        
        if save_path:
            if save_path.lower().endswith(".wav"):
                format = "wav"
            elif save_path.lower().endswith(".mp3"):
                format = "mp3"
            else:
                format = "mp3"
                
            self.AudioProcessor.export_audio(save_path, format)
            print_success(f"Audio exported to {save_path}")
            
    def send_prompt(self):
        self.save_state()

        if not hasattr(self.AudioProcessor, "audio") or self.AudioProcessor.audio is None:
            print_fail("No audio loaded.")
            return
        
        text = self.entry.get()
        full_prompt = f"You are a audio editing AI. You are controllable via natural language and editing a audio file. The audio file is {round(self.AudioProcessor.get_lenght())}s long."
        if whisper_support:
            if self.use_transcript_checkbox.get():
                if not self.whisper:
                    messagebox.showinfo("Info", "Loading Whisper model. This may take a few minutes depending on your internet connection. See the progress in your command line. If this window appears to be frozen, the transcription is running.")
                    self.whisper = transcribe.Whisper()
                transcript = self.whisper.transcribe(self.AudioProcessor.audio_path)
                full_prompt += f"\nThis is a transcript with per word timestamps of the audio:\n{transcript}"
        full_prompt += f"\n\nUser Prompt: {text}"
        self.entry.delete(0, "end")
        
        function_call, text_result = self.gemini.generate(full_prompt)
        
        if function_call:
            print_info(f"Gemini called {function_call.name}")
            if function_call.name == "cut_audio":
                print_info("Cut function called")
                args = function_call.args
                result = self.AudioProcessor.cut(args["start"], args["end"])
                if not result:
                    messagebox.showerror("Error", "Please try again.")
            self.update_plot()
        elif text_result:
            messagebox.showerror("Error", text_result.strip())
        else:
            print_fail("Gemini returned no data")

    def save_state(self):
        if hasattr(self.AudioProcessor, "audio") and self.AudioProcessor.audio is not None:
            self.last_states.append(self.AudioProcessor.audio._spawn(self.AudioProcessor.audio.raw_data))
            if len(self.last_states) > 10:
                self.last_states.pop(0) 
           
    def undo_last(self):
        if len(self.last_states) == 0:
            print_warn("No previous states to undo")
            messagebox.showwarning("Warning", "No previous states to undo")
            return
        
        self.AudioProcessor.audio = self.last_states.pop()
        self.update_plot()
        print_info("Undid last action")

    def run(self):
        self.root.mainloop()
        
def main():
    app = CuttedApp()
    app.run()
