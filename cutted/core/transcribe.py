import json
import whisper_timestamped as whisper

class Whisper:
    def __init__(self, model_size: str = "small", device: str = "cpu"):
        self.model = whisper.load_model(
            model_size, device=device
        )
        
    def transcribe(self, file_path: str):
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
        readable += (f'Text: {result["text"].strip()} \n\n')
        readable += (f'Segments: {result["segments"]}')
        
        return result, readable