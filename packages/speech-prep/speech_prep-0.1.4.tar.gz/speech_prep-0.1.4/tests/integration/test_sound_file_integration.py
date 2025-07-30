"""Integration tests for SoundFile class using real files and no mocks."""

import shutil

import pytest

from speech_prep.core import SoundFile
from speech_prep.exceptions import SpeechPrepError

# Skip the entire module if ffmpeg is not installed
pytestmark = pytest.mark.skipif(
    shutil.which("ffmpeg") is None, reason="ffmpeg is required for integration tests"
)


@pytest.fixture
def check_audio_file_exists(audio_file_with_silence):
    """Ensure the test audio file exists before running tests."""
    file_path, _ = audio_file_with_silence
    if not file_path.exists():
        pytest.skip(f"Test audio file {file_path} not found")
    return file_path


class TestSoundFileIntegrationWithRealFiles:
    """
    Integration tests for SoundFile class using real files and no mocks.

    These tests verify that the SoundFile class works correctly with real audio files
    and the actual implementations of its dependencies.
    """

    def test_soundfile_initialization(self, check_audio_file_exists):
        """Test SoundFile initialization with a real audio file."""
        # Get the real audio file
        file_path = check_audio_file_exists

        # Create a SoundFile instance without any mocks
        sound_file = SoundFile(file_path)

        # Verify basic properties
        assert sound_file.path == file_path
        assert sound_file.duration > 0
        assert sound_file.format is not None
        from speech_prep.formats import AudioFormat

        assert isinstance(sound_file.format, AudioFormat)
        assert sound_file.file_size > 0

        # Verify silence detection
        assert isinstance(sound_file.silence_periods, list)

        # Print debug info
        print(f"File: {file_path}")
        print(f"Duration: {sound_file.duration}")
        print(f"Format: {sound_file.format}")
        print(f"File size: {sound_file.file_size}")
        print(f"Silence periods: {len(sound_file.silence_periods)}")

    def test_full_processing_pipeline(self, check_audio_file_exists, temp_dir):
        """
        Test a complete processing pipeline with real operations.

        This test performs:
        1. SoundFile initialization
        2. Silence stripping
        3. Speed adjustment
        4. Format conversion

        No functions are mocked, so this is a true integration test.
        """
        # Get the real audio file
        input_path = check_audio_file_exists

        # Define paths for outputs
        stripped_path = temp_dir / "real_stripped.wav"
        sped_path = temp_dir / "real_sped.wav"
        converted_path = temp_dir / "real_final.mp3"

        # Create initial SoundFile
        original = SoundFile(input_path)
        print(f"Original file: {original}")

        # 1. Strip silence
        stripped = original.strip(stripped_path)
        assert stripped is not None, "Strip operation failed"
        assert stripped.path.exists(), "Stripped file doesn't exist"
        assert (
            stripped.duration <= original.duration
        ), "Stripped file should be shorter or equal"
        print(f"Stripped file: {stripped}")

        # 2. Adjust speed
        speed_factor = 1.5
        sped = stripped.speed(sped_path, speed_factor)
        assert sped is not None, "Speed operation failed"
        assert sped.path.exists(), "Sped file doesn't exist"
        # Duration should be approximately 1/speed_factor of the original
        # Allow for some tolerance due to encoding differences
        expected_duration = stripped.duration / speed_factor
        tolerance = 0.2  # 20% tolerance
        assert (
            abs(sped.duration - expected_duration) <= expected_duration * tolerance
        ), f"Speed adjustment incorrect: {sped.duration} vs {expected_duration}"
        print(f"Sped file: {sped}")

        # 3. Convert format
        from speech_prep.formats import AudioFormat

        converted = sped.convert(converted_path, AudioFormat.MP3, audio_bitrate="192k")
        assert converted is not None, "Convert operation failed"
        assert converted.path.exists(), "Converted file doesn't exist"
        assert converted.format == AudioFormat.MP3, "Format conversion failed"
        print(f"Converted file: {converted}")

        # Verify final file properties
        assert converted.duration > 0, "Final file has no duration"
        assert converted.file_size > 0, "Final file has no size"

    def test_error_handling_with_real_files(self, temp_dir):
        """Test error handling with real but problematic files."""
        # Create an empty file (which will cause processing errors)
        empty_file = temp_dir / "empty.wav"
        empty_file.touch()

        # Attempt to create a SoundFile from the empty file
        with pytest.raises(SpeechPrepError) as exc_info:
            SoundFile(empty_file)

        assert "Failed to extract metadata" in str(
            exc_info.value
        ), "Empty file should raise metadata extraction error"
