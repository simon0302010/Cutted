
import pytest
from cutted.core.audio_processor import AudioProcessor

def test_load_audio():
    processor = AudioProcessor()
    processor.load_audio("tests/test_audio.mp3")
    assert processor.audio is not None
