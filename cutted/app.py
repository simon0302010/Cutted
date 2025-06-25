import customtkinter

def load_file():
    file_path = customtkinter.filedialog.askopenfilenames(
        filetypes=[("Audio files", ".mp3 .wav .aac .flac .ogg .m4a")]
    )
    print(list(file_path))

def main():
    root = customtkinter.CTk()
    root.title("Cutted")
    root.geometry("600x400")

    button = customtkinter.CTkButton(root, text="Load audio", command=load_file)
    button.pack()

    root.mainloop()