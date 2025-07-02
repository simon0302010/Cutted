import threading
import time
import tkinter.messagebox as messagebox

import customtkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .core import audio_processor, gemini
from .core.logger import print_fail, print_info, print_success, print_warn

customtkinter.set_appearance_mode("Dark")

try:
    from .core import transcribe

    whisper_support = True
    print_info("Whisper support present.")
except ModuleNotFoundError:
    whisper_support = False
    print_info("Whisper support is not present.")


class CuttedApp:
    def __init__(self):
        self.AudioProcessor = audio_processor.AudioProcessor()
        self.AudioProcessor._init_pygame()
        if whisper_support:
            self.whisper = None
        self.gemini = gemini.GeminiClient()
        self.canvas = None
        self.cursor_line = None
        self.last_slider_update = 0
        self.slider_value = 0
        self.playback_start_time = 0
        self.is_playing = False
        self.last_states = []
        self.setup_ui()

    def setup_ui(self):
        self.root = customtkinter.CTk()
        self.root.title("Cutted")
        self.root.geometry("600x400")

        self.root.bind("<Configure>", self.on_resize)

        self.use_history_var = customtkinter.BooleanVar(value=False)

        self.plot_frame = customtkinter.CTkFrame(
            self.root, height=250, fg_color="transparent"
        )
        self.plot_frame.pack(
            side=customtkinter.TOP,
            fill=customtkinter.BOTH,
            expand=True,
            padx=20,
            pady=(20, 150),
        )
        self.plot_frame.pack_propagate(False)

        button = customtkinter.CTkButton(
            self.root, text="Load audio", command=self.select_file
        )
        button.place(relx=0.5, rely=1.0, anchor="s", y=-30)

        export_button = customtkinter.CTkButton(
            self.root, text="Export", command=self.export_audio, width=70
        )
        export_button.place(relx=0.9, rely=1.0, anchor="s", y=-30)

        undo_button = customtkinter.CTkButton(
            self.root, text="Undo", command=self.undo_last, width=70
        )
        undo_button.place(relx=0.1, rely=1.0, anchor="s", y=-30)

        if whisper_support:
            self.use_transcript_checkbox = customtkinter.CTkCheckBox(
                self.root,
                text="Send transcript to Gemini (slower, more accurate)",
                text_color="#888888",
                font=("Arial", 12),
            )
            self.use_transcript_checkbox.place(relx=0.0, rely=1.0, anchor="w", y=-12)

        self.use_audio_checkbox = customtkinter.CTkCheckBox(
            self.root,
            text="Send audio to Gemini (buggy)",
            text_color="#888888",
            font=("Arial", 12),
        )
        self.use_audio_checkbox.place(relx=1.0, rely=1.0, anchor="e", y=-12)

        self.play_button = customtkinter.CTkButton(
            self.root, text="Play", command=self.play_audio, width=50
        )
        self.play_button.place(relx=0.3, rely=1.0, anchor="s", y=-30)
        self.stop_button = customtkinter.CTkButton(
            self.root, text="Stop", command=self.stop_audio, width=50
        )
        self.stop_button.place(relx=0.7, rely=1.0, anchor="s", y=-30)

        self.input_frame = customtkinter.CTkFrame(
            self.root, fg_color="transparent", height=36
        )
        self.input_frame.place(relx=0.5, rely=1.0, anchor="s", y=-90, relwidth=0.8)

        settings_button = customtkinter.CTkButton(
            self.input_frame,
            text="⚙",
            command=self.open_settings,
            width=36,
            height=36,
            font=("Arial", 18),
        )
        settings_button.pack(side="left", padx=(0, 5))

        self.entry = customtkinter.CTkEntry(self.input_frame, height=32)
        self.entry.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.send_button = customtkinter.CTkButton(
            self.input_frame, text="➤", width=36, height=36, command=self.send_prompt
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
        if hasattr(self, "slider") and self.slider is not None:
            self.slider.destroy()

        fig, _ = self.AudioProcessor.plot_audio()
        self.ax = fig.axes[0]
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()

        self.audio_length = float(self.AudioProcessor.get_length())

        slider_width = self.root.winfo_width() - 40
        if self.slider_value > self.audio_length:
            self.slider_value = self.audio_length
        if self.slider_value < 0:
            self.slider_value = 0

        self.slider = customtkinter.CTkSlider(
            self.root,
            from_=0,
            to=self.audio_length,
            command=self.set_cursor,
            width=slider_width,
        )
        self.slider.set(self.slider_value)
        self.slider.place(relx=0.5, rely=1.0, anchor="s", y=-130)
        self.set_cursor(self.slider_value)

        self.canvas.get_tk_widget().pack(
            fill=customtkinter.BOTH,
            expand=True,
            padx=10,
            pady=10,
        )

        self.cursor_line = self.ax.axvline(
            x=self.slider_value, color="red", linewidth=2
        )
        self.canvas.draw_idle()

    def show_spinner(self, message="Transcribing..."):
        spinner_win = customtkinter.CTkToplevel(self.root)
        spinner_win.title("Please wait")
        spinner_win.geometry("250x100")
        spinner_win.grab_set()
        spinner_win.resizable(False, False)
        label = customtkinter.CTkLabel(spinner_win, text=message)
        label.pack(pady=10)
        progress = customtkinter.CTkProgressBar(spinner_win, mode="indeterminate")
        progress.pack(pady=10, padx=20, fill="x")
        progress.start()
        return spinner_win, progress

    def set_cursor(self, value):
        now = time.time()
        if now - self.last_slider_update < 0.05:  # 100ms
            return
        self.last_slider_update = now

        self.slider_value = round(value, 2)

        if self.cursor_line:
            self.cursor_line.set_xdata([self.slider_value, self.slider_value])
            self.canvas.draw_idle()
            self.slider.set(self.slider_value)
            self.set_cursor(self.slider_value)

        print_info(f"Slider Value: {self.slider_value}")

    def play_audio(self):
        if (
            not hasattr(self.AudioProcessor, "audio")
            or self.AudioProcessor.audio is None
        ):
            print_fail("No audio loaded.")
            messagebox.showwarning("Warning", "No audio loaded.")
            return

        start_time = self.slider.get() if hasattr(self, "slider") else 0
        self.playback_start_time = start_time
        self.AudioProcessor.play_audio(start_time)

    def stop_audio(self):
        rel_pos = self.AudioProcessor.stop_audio()
        self.is_playing = False
        abs_pos = self.playback_start_time + rel_pos
        self.slider.set(abs_pos)
        self.set_cursor(abs_pos)
        print_info(f"Absolute position in audio: {abs_pos:.2f}s")

    def export_audio(self):
        if (
            not hasattr(self.AudioProcessor, "audio")
            or self.AudioProcessor.audio is None
        ):
            print_fail("No audio loaded.")
            messagebox.showwarning("Warning", "No audio loaded.")
            return

        save_path = customtkinter.filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[
                ("MP3 files", "*.mp3"),
                ("WAV files", "*.wav"),
            ],
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

    def open_settings(self):
        settings_window = customtkinter.CTkToplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("300x200")

        use_history = customtkinter.CTkCheckBox(
            settings_window,
            text="Use chat history (Can produce errors)",
            variable=self.use_history_var,
        )
        use_history.pack(pady=10)

    def send_prompt(self):
        print(self.AudioProcessor.get_waveform_summary())
        self.save_state()

        if (
            not hasattr(self.AudioProcessor, "audio")
            or self.AudioProcessor.audio is None
        ):
            print_fail("No audio loaded.")
            messagebox.showwarning("Warning", "No audio loaded.")
            return

        text = self.entry.get()
        if not text.strip():
            return

        def after_transcribe(transcript):
            full_prompt = (
                f"You are a audio editing AI. You are controllable via natural language and editing a audio file. The audio file is {round(self.AudioProcessor.get_length(), 2)}s long. The cursor of the user is currently at {self.slider_value}s."
                "\nHere is a the waveform samples of the audio. You can use them to determine silent parts, loud parts, silences, beats and much more.\nYou are forced to used these if the user requires you to cut out silent of quiet parts for example."
                "\nAll of your tools should be enough to fullfill almost every task.\nNEVER ASK FOR CONFIRMATION FROM THE USER. DO EVERYTHING!"
                f"\n{self.AudioProcessor.get_waveform_summary()}\n"
            )
            if transcript:
                full_prompt += f"\nThis is a transcript with per word timestamps of the audio:\n{transcript}"
                full_prompt += "\nThe transcript likely has issues. If you need infos about some words they might just be misspelled in the audio."
            full_prompt += f"\n\nUser Prompt: {text}"
            self.entry.delete(0, "end")

            if self.use_audio_checkbox.get():
                function_call, text_result = self.gemini.generate(
                    full_prompt,
                    audio_base64=self.AudioProcessor.get_audio_base64(),
                    use_history=self.use_history_var.get(),
                )
            else:
                function_call, text_result = self.gemini.generate(
                    full_prompt, use_history=self.use_history_var.get()
                )

            if function_call:
                print_info(f"Gemini called {function_call.name}")
                if function_call.name == "cut_audio":
                    print_info("Cut function called")
                    args = function_call.args
                    result = self.AudioProcessor.cut(args["start"], args["end"])
                    if not result:
                        messagebox.showerror("Error", "Please try again.")
                if function_call.name == "change_volume":
                    print_info("Change Volume function called")
                    args = function_call.args
                    result = self.AudioProcessor.change_volume(
                        args["start"], args["end"], args["volume"]
                    )
                    if not result:
                        messagebox.showerror("Error", "Please try again.")
                self.update_plot()
            elif text_result:
                messagebox.showerror("Error", text_result.strip())
            else:
                messagebox.showerror("Error", "Gemini returned no data")
                print_fail("Gemini returned no data")

        if whisper_support and self.use_transcript_checkbox.get():
            if not self.whisper:
                messagebox.showinfo(
                    "Info",
                    "Loading Whisper model. This may take a few minutes depending on your internet connection. See the progress in your command line. If this window appears to be frozen, the transcription is running. Press OK to continue.",
                )
                self.whisper = transcribe.Whisper()

            spinner_win, _ = self.show_spinner("Transcribing...")

            def transcribe_thread():
                _, transcript = self.whisper.transcribe(self.AudioProcessor.audio_path)
                self.root.after(
                    0, lambda: (spinner_win.destroy(), after_transcribe(transcript))
                )

            threading.Thread(target=transcribe_thread, daemon=True).start()
            return

        after_transcribe(None)

    def save_state(self):
        if (
            hasattr(self.AudioProcessor, "audio")
            and self.AudioProcessor.audio is not None
        ):
            self.last_states.append(
                self.AudioProcessor.audio._spawn(self.AudioProcessor.audio.raw_data)
            )
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
