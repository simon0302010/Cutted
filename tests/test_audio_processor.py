import pytest
from cutted.core.audio_processor import AudioProcessor

@pytest.fixture
def audio_processor():
    processor = AudioProcessor()
    processor.load_audio("tests/test_audio.mp3")
    return processor

def test_load_audio(audio_processor):
    assert audio_processor.audio is not None

def test_get_length(audio_processor):
    assert 29.9 < audio_processor.get_length() < 30.1

def test_cut(audio_processor):
    original_length = audio_processor.get_length()
    audio_processor.cut([5], [10])
    assert audio_processor.get_length() < original_length

def test_change_volume(audio_processor):
    original_audio = audio_processor.audio
    audio_processor.change_volume([0], [5], [2.0])
    assert audio_processor.audio != original_audio