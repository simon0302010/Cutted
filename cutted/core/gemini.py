import os
import sys
import base64
from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Please set the environment variable GEMINI_API_KEY to your Gemini API Key.")
    sys.exit(0)

class GeminiClient:
    def __init__(self):
        self.client = genai.Client(
            api_key=GEMINI_API_KEY,
        )
        self.contents = []
    
    def generate(self, prompt: str, model: str = "gemini-2.0-flash", audio_base64 = None, use_history = 0):
        if not use_history:
            self.contents = []
        
        parts=[
            types.Part.from_text(text=prompt),
        ]
        
        if audio_base64:
            parts.append(types.Part.from_bytes(
                mime_type="audio/mpeg",
                data=base64.b64decode(audio_base64)
            ))
        
        self.contents.append(
            types.Content(
                role="user",
                parts=parts
            )
        )
        tools = [
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name="cut_audio",
                        description=(
                            "Remove one or more segments from the audio by specifying start and end times in seconds. "
                            "You can cut multiple segments at once by providing lists of start and end values. "
                            "Each segment defined by a start and end pair will be removed from the audio."
                        ),
                        parameters=genai.types.Schema(
                            type=genai.types.Type.OBJECT,
                            required=["start", "end"],
                            properties={
                                "start": genai.types.Schema(
                                    type=genai.types.Type.ARRAY,
                                    items=genai.types.Schema(
                                        type=genai.types.Type.NUMBER,
                                    ),
                                ),
                                "end": genai.types.Schema(
                                    type=genai.types.Type.ARRAY,
                                    items=genai.types.Schema(
                                        type=genai.types.Type.NUMBER,
                                    ),
                                ),
                            },
                        ),
                    ),
                    types.FunctionDeclaration(
                        name="change_volume",
                        description=(
                            "Adjust the volume of specific segments in the audio by specifying lists of start times, end times, "
                            "and volume factors. Each segment between a start and end time will have its volume changed by the "
                            "corresponding factor (e.g., 0.5 for half volume, 2.0 for double volume). Multiple segments can be "
                            "adjusted at once by providing lists of values."
                        ),
                        parameters=genai.types.Schema(
                            type=genai.types.Type.OBJECT,
                            required=["start", "end", "volume"],
                            properties={
                                "start": genai.types.Schema(
                                    type=genai.types.Type.ARRAY,
                                    items=genai.types.Schema(
                                        type=genai.types.Type.NUMBER,
                                    ),
                                ),
                                "end": genai.types.Schema(
                                    type=genai.types.Type.ARRAY,
                                    items=genai.types.Schema(
                                        type=genai.types.Type.NUMBER,
                                    ),
                                ),
                                "volume": genai.types.Schema(
                                    type=genai.types.Type.ARRAY,
                                    items=genai.types.Schema(
                                        type=genai.types.Type.NUMBER,
                                    ),
                                ),
                            },
                        ),
                    ),
                ]
            )
        ]
        generate_content_config = types.GenerateContentConfig(
            tools=tools,
            response_mime_type="text/plain",
        )

        response = self.client.models.generate_content(
            model=model,
            contents=self.contents,
            config=generate_content_config,
        )

        function_call = None
        text_response = None
        try:
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if part.function_call:
                        function_call = part.function_call
                    if part.text:
                        text_response = part.text
        except TypeError:
            pass
        
        model_parts = []
        if text_response:
            model_parts.append(
                types.Part.from_text(text=text_response)
            )
        if function_call:
            model_parts.append(
                types.Part.from_function_call(
                    name=function_call.name,
                    args=function_call.args
                )
            )
            
        self.contents.append(
            types.Content(
                role="model",
                parts=model_parts
            )
        )

        return function_call, text_response
        
if __name__ == "__main__":
    gemini = GeminiClient()
    print(gemini.generate("cut from 10 to 20.5"))