import customtkinter
from .core.logger import *
from .core import audio_processor

from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure

def select_file():
    global AudioProcessor, root, plot_frame
    file_path = customtkinter.filedialog.askopenfilename(
        filetypes=[("Audio files", ".mp3 .wav .aac .flac .ogg .m4a")]
    )
    AudioProcessor.load_audio(file_path)
    fig = AudioProcessor.plot_audio()
    
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    
    canvas.get_tk_widget().pack(fill=customtkinter.BOTH, expand=True)

def main():
    global root, plot_frame
    root = customtkinter.CTk()
    root.title("Cutted")
    root.geometry("600x400")
    
    plot_frame = customtkinter.CTkFrame(root, height=250)
    plot_frame.pack(side=customtkinter.TOP, fill=customtkinter.X, padx=10, pady=10)
    plot_frame.pack_propagate(False)
    
    button = customtkinter.CTkButton(root, text="Load audio", command=select_file)
    button.place(relx=0.5, rely=1.0, anchor="s", y=-30)

    global AudioProcessor
    AudioProcessor = audio_processor.AudioProcessor()

    root.mainloop()