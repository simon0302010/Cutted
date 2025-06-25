import customtkinter
from .core.logger import *
from .core import audio_processor

from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure

customtkinter.set_appearance_mode("Dark")

class CuttedApp:
    def __init__(self):
        self.AudioProcessor = audio_processor.AudioProcessor()
        self.canvas = None
        self.setup_ui()
    
    def setup_ui(self):
        self.root = customtkinter.CTk()
        self.root.title("Cutted")
        self.root.geometry("600x400")
        
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
    
    def select_file(self):
        file_path = customtkinter.filedialog.askopenfilename(
            filetypes=[("Audio files", ".mp3 .wav .aac .flac .ogg .m4a")]
        )
        if file_path:
            self.AudioProcessor.load_audio(file_path)
            self.update_plot()
            
    def set_cursor(self, value):
        value = round(value)
        print(f"Slider Value: {value}")

    def update_plot(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        
        fig = self.AudioProcessor.plot_audio()
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        
        self.audio_lenght = int(round(self.AudioProcessor.get_lenght()))
        self.slider = customtkinter.CTkSlider(
            self.root, from_=0, to=self.audio_lenght, command=self.set_cursor, width=500
        )
        
        self.slider.place(relx=0.5, rely=1.0, anchor="s", y=-130)
        
        self.canvas.get_tk_widget().pack(
            fill=customtkinter.BOTH, 
            expand=True, 
            padx=10,
            pady=10,
        )
    
    def run(self):
        self.root.mainloop()
        
def main():
    app = CuttedApp()
    app.run()