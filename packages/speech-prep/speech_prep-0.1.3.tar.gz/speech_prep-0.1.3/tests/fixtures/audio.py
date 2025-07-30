"""Test fixtures for speech_prep."""

from collections.abc import Generator
from pathlib import Path
import tempfile

from pydub import AudioSegment
from pydub.generators import Sine
import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def audio_file_with_silence(
    temp_dir: Path,
) -> Generator[tuple[Path, float], None, None]:
    """
    Create a test audio file with known silence periods.

    Returns a tuple of (file_path, duration) where duration is in seconds.

    The generated file has 5 seconds structure:
    - 1s speech (sine wave at 440Hz)
    - 1s silence
    - 1s speech (sine wave at 880Hz)
    - 1s silence
    - 1s speech (sine wave at 440Hz)
    """
    # Generate a simple audio pattern
    speech1 = Sine(440).to_audio_segment(duration=1000)  # 1 second at 440Hz
    silence = AudioSegment.silent(duration=1000)  # 1 second of silence
    speech2 = Sine(880).to_audio_segment(duration=1000)  # 1 second at 880Hz

    # Combine segments to create a file with known silence periods
    audio = speech1 + silence + speech2 + silence + speech1

    # Save to temp file
    file_path = temp_dir / "test_audio.wav"
    audio.export(str(file_path), format="wav")

    # The total duration is 5 seconds
    duration = 5.0

    yield file_path, duration

    # Cleanup happens automatically due to the temp_dir fixture


@pytest.fixture
def audio_file_no_silence(temp_dir: Path) -> Generator[tuple[Path, float], None, None]:
    """
    Create a test audio file with no silence periods.

    Returns a tuple of (file_path, duration) where duration is in seconds.
    """
    # Generate 3 seconds of continuous sound
    audio = Sine(440).to_audio_segment(duration=3000)  # 3 seconds at 440Hz

    # Save to temp file
    file_path = temp_dir / "test_audio_no_silence.wav"
    audio.export(str(file_path), format="wav")

    # The total duration is 3 seconds
    duration = 3.0

    yield file_path, duration
