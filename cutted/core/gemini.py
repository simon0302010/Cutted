import os
from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Please set the environment variable GEMINI_API_KEY to your Gemini API Key.")