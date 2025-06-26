import os
import sys
from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Please set the environment variable GEMINI_API_KEY to your Gemini API Key.")
    sys.exit(0)

def generate():
    client = genai.Client(
        api_key=GEMINI_API_KEY,
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""cut from 10 to 20 seconds and from 50 to 60"""),
            ],
        ),
        types.Content(
            role="model",
            parts=[
                types.Part.from_function_call(
                    name="""cut_audio""",
                    args={"end":[20,60],"start":[10,50]},
                ),
            ],
        ),
        types.Content(
            role="user",
            parts=[
                types.Part.from_function_response(
                    name="""cut_audio""",
                    response={
                      "output": """success""",
                    },
                ),
                types.Part.from_text(text=str(input("Prompt: "))),
            ],
        ),
    ]
    tools = [
        types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name="cut_audio",
                    description="Cuts specified parts out of audio. Multiple parts can be cut if a list of both start and end values is used as property.",
                    parameters=genai.types.Schema(
                        type = genai.types.Type.OBJECT,
                        required = ["start", "end"],
                        properties = {
                            "start": genai.types.Schema(
                                type = genai.types.Type.ARRAY,
                                items = genai.types.Schema(
                                    type = genai.types.Type.NUMBER,
                                ),
                            ),
                            "end": genai.types.Schema(
                                type = genai.types.Type.ARRAY,
                                items = genai.types.Schema(
                                    type = genai.types.Type.NUMBER,
                                ),
                                ),
                        },
                    ),
                ),
            ])
    ]
    generate_content_config = types.GenerateContentConfig(
        tools=tools,
        response_mime_type="text/plain",
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )

    function_call = None
    text_response = None
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.function_call:
                function_call = part.function_call
            if part.text:
                text_response = part.text

    if text_response:
        print(f"Text: {text_response}\n")
    if function_call:
        print(f"Function Call: {function_call}")

if __name__ == "__main__":
    generate()
