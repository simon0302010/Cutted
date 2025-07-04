![PyPI](https://img.shields.io/pypi/v/cutted?color=blue)
![PyPI - License](https://img.shields.io/pypi/l/lyriks-video)


<div align="left">
  <a href="https://shipwrecked.hackclub.com/?t=ghrm" target="_blank">
    <img src="https://hc-cdn.hel1.your-objectstorage.com/s/v3/739361f1d440b17fc9e2f74e49fc185d86cbec14_badge.png" 
         alt="This project is part of Shipwrecked, the world's first hackathon on an island!" 
         style="width: 35%;">
  </a>
</div>


# Cutted

**Cutted** is an AI-powered audio editor you control with natural language.

- Cut, trim, or adjust volume by typing what you want
- Detect and remove silence or loud parts automatically
- Transcribe audio (with Whisper)
- Undo edits, export as MP3 or WAV

## Install

1. Make sure your Python interpreter has [Tkinter support](https://stackoverflow.com/questions/5459444/tkinter-python-may-not-be-configured-for-tk)
2. Make sure [FFmpeg](https://ffmpeg.org/) is installed.
3. Install Cutted:
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

## Usage Examples

### Basic Editing

- **Cut a segment:**
  ```
  cut from 10 to 20
  ```
  Removes audio between 10s and 20s.

- **Remove multiple segments:**
  ```
  cut from 5 to 7 and from 15 to 18
  ```

- **Change volume:**
  ```
  make 0 to 5 seconds twice as loud
  ```
  or
  ```
  reduce volume from 10 to 12 by half
  ```

- **Remove silence:**
  ```
  remove all silent parts
  ```
  > Note: Removing silence is experimental and can be buggy or produce bad results in some cases.

- **Undo last edit:**  
  Click the "Undo" button.

- **Export your result:**  
  Click the "Export" button and choose MP3 or WAV.

### Advanced: Using Whisper Transcription

If you install with Whisper support and enable "Send transcript to Gemini" in the UI, you can use commands like:

- **Cut by word or sentence:**
  ```
  cut when I say the word hello
  ```
  or
  ```
  cut the sentence "welcome to the show"
  ```
  > This uses Whisper to transcribe your audio and allows precise editing based on spoken words or phrases.

### Audio-to-Gemini (Experimental)

If you enable "Send audio to Gemini" (checkbox), you can also use word-based commands, but accuracy is much lower compared to using Whisper.

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
