![PyPI](https://img.shields.io/pypi/v/cutted?color=blue)
![PyPI - License](https://img.shields.io/pypi/l/lyriks-video)

# Cutted

**Cutted** is an AI-powered audio editor you control with natural language.

- Cut, trim, or adjust volume by typing what you want
- Detect and remove silence or loud parts automatically
- Transcribe audio (with Whisper)
- Undo edits, export as MP3 or WAV

## Install

1. Make sure [FFmpeg](https://ffmpeg.org/) is installed.
2. Install Cutted:
   ```bash
   pip install cutted
   ```
   With Whisper support:
   ```bash
   pip install cutted[whisper]
   ```

## Usage

```bash
python -m cutted
```
Load an audio file, enter your command in plain English, and export your result.  
You can also enable or disable chat history for smarter follow-up actions in the settings menu (gear icon).

---

## Gemini API Key

Set your Gemini API key as an environment variable before running Cutted:

**Linux/macOS:**
```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your-gemini-api-key
```

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your-gemini-api-key"
```