import base64
import io

import numpy as np
import pygame
from matplotlib.figure import Figure
from pydub import AudioSegment
from pydub.utils import ratio_to_db

from .logger import print_fail, print_info, print_success, print_warn


class AudioProcessor:
    def __init__(self):
        self.audio_path = None
        self.audio = None
        self.is_playing_var = False
        self.play_thread = None
        self._init_pygame()

    def _init_pygame(self):
        try:
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
            pygame.mixer.init()
            print_success("Pygame initialized")
        except pygame.error as e:
            print_warn(f"Pygame initialization warning: {e}")

    def load_audio(self, audio_path: str, volume: float = 1.0):
        self.audio_path = audio_path
        self.audio = AudioSegment.from_file(self.audio_path)
        self.audio = self.audio.apply_gain(ratio_to_db(volume))
        print_info(f"Loaded {self.audio_path}")

    def plot_audio(self):
        if self.audio is None:
            print_fail("No audio loaded.")
            return

        samples = np.array(self.audio.get_array_of_samples())
        if self.audio.channels == 2:
            samples = samples.reshape((-1, 2))
            samples = samples.mean(axis=1)

        samples = samples / np.max(np.abs(samples))

        times = np.linspace(0, len(samples) / self.audio.frame_rate, num=len(samples))

        fig = Figure(figsize=(5, 4), facecolor="#242424")
        ax = fig.add_subplot()
        ax.set_facecolor("#242424")
        (line,) = ax.plot(times, samples, color="cyan", linewidth=1.5)

        # remove text
        ax.set_title("")
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_yticks([])

        ax.margins(0)
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        ax.set_xlim(times[0], times[-1])
        ax.set_ylim(np.min(samples), np.max(samples))

        return fig

    def get_waveform_summary(self):
        num_samples = round(self.get_length())
        if self.audio is None:
            return "No audio loaded."
        samples = np.array(self.audio.get_array_of_samples())
        if self.audio.channels == 2:
            samples = samples.reshape((-1, 2))
            samples = samples.mean(axis=1)
        samples = samples / np.max(np.abs(samples))
        indices = np.linspace(0, len(samples) - 1, num_samples).astype(int)
        summary = samples[indices]
        return f"Waveform samples (normalized, {num_samples} points):\n" + " ".join(
            f"{x:.2f}" for x in summary
        )

    def get_length(self):
        self.duration = self.audio.duration_seconds
        self.duration = round(self.duration, 2)
        return self.duration

    def cut(self, start, end):
        if len(start) == len(end):
            if len(start) == 1:
                single_start = max(0, start[0])
                single_end = max(0, end[0])
                if single_end <= single_start:
                    print_fail("End time must be greater than start time.")
                    return False
                print_info(f"Cutting from {single_start} to {single_end}")
                start_ms = round(single_start * 1000)
                end_ms = round(single_end * 1000)
                self.audio = self.audio[:start_ms] + self.audio[end_ms:]
                return True
            else:
                time_sets = list(zip(start, end))
                subtract_time = 0
                for single_start, single_end in time_sets:
                    single_start = max(0, single_start - subtract_time)
                    single_end = max(0, single_end - subtract_time)
                    if single_end <= single_start:
                        print_fail("End time must be greater than start time.")
                        continue
                    print_info(f"Cutting from {single_start} to {single_end}")
                    start_ms = round(single_start * 1000)
                    end_ms = round(single_end * 1000)
                    self.audio = self.audio[:start_ms] + self.audio[end_ms:]
                    subtract_time += single_end - single_start
                return True
        else:
            return False

    def change_volume(self, start, end, volume):
        if len(start) == len(end) == len(volume):
            time_sets = list(zip(start, end, volume))
            for single_start, single_end, single_volume in time_sets:
                if single_end <= single_start:
                    print_fail("End time must be greater than start time.")
                    continue
                print_info(
                    f"Changing volume of {single_start} - {single_end} to {str(single_volume)}"
                )

                start_ms = round(single_start * 1000)
                end_ms = round(single_end * 1000)
                part1 = self.audio[:start_ms]
                part2 = self.audio[start_ms:end_ms]
                part3 = self.audio[end_ms:]

                part2 = part2.apply_gain(ratio_to_db(single_volume))

                self.audio = part1 + part2 + part3
            return True
        else:
            return False

    def play_audio(self, start_time=0):
        if self.audio is None:
            print_fail("No audio loaded.")
            return False

        try:
            self.stop_audio()

            start_ms = int(start_time * 1000)
            audio_segment = self.audio[start_ms:]

            audio_segment = audio_segment.set_frame_rate(22050)
            audio_segment = audio_segment.set_channels(2)
            audio_segment = audio_segment.set_sample_width(2)

            audio_data = io.BytesIO()
            audio_segment.export(audio_data, format="wav")
            audio_data.seek(0)

            pygame.mixer.music.load(audio_data)
            pygame.mixer.music.play()
            self.is_playing_var = True

            print_success(f"Playing audio from {start_time}s")
            return True

        except Exception as e:
            print_fail(f"Error playing audio: {e}")
            return False

    def stop_audio(self):
        try:
            if pygame.mixer.get_init():
                pos_ms = pygame.mixer.music.get_pos()
                pos_sec = pos_ms / 1000 if pos_ms >= 0 else 0
                pygame.mixer.music.stop()
                self.is_playing_var = False
                print_info(f"Audio playback stopped at {pos_sec:.2f}s")
                return pos_sec
        except Exception as e:
            print_warn(f"Error stopping audio: {e}")
            return 0

    def is_playing(self):
        try:
            if pygame.mixer.get_init():
                return pygame.mixer.music.get_busy()
            return False
        except:
            return False

    def get_audio_info(self):
        if self.audio is None:
            return None

        return {
            "duration": self.get_length(),
            "channels": self.audio.channels,
            "frame_rate": self.audio.frame_rate,
            "sample_width": self.audio.sample_width,
        }

    def export_audio(self, path, format: str = "mp3"):
        self.audio.export(path, format=format)

    def get_audio_base64(self):
        buffer = io.BytesIO()
        self.audio.export(buffer, format="mp3")
        buffer.seek(0)
        audio_bytes = buffer.read()
        audio_base64 = base64.b64encode(audio_bytes)
        return audio_base64
