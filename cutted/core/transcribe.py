import json
import tkinter.messagebox as messagebox

import whisper_timestamped as whisper

from .logger import print_warn


class Whisper:
    def __init__(self, model_size: str = "small", device=None):
        self.model = whisper.load_model(model_size, device=device)

    def transcribe(self, file_path: str):
        try:
            audio = whisper.load_audio(file_path)

            result = whisper.transcribe_timestamped(self.model, audio)

            result = json.loads(json.dumps(result))

            segments_new = []
            for segment in result["segments"]:
                segment.pop("seek", None)
                segment.pop("tokens", None)
                segment.pop("temperature", None)
                segment.pop("avg_logprob", None)
                segment.pop("compression_ratio", None)

                segments_new.append(segment)

            readable = ""
            readable += f'Text: {result["text"].strip()} \n\n'
            readable += f'Segments: {result["segments"]}'
        except Exception as e:
            print_warn(f"An error occured while transcribing: {e}")
            messagebox.showwarning(f"An error occured while transcribing: {e}")

        return result, readable
