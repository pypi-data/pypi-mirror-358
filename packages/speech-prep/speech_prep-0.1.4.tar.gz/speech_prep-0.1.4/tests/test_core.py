"""Unit tests for the core module."""

from pathlib import Path

import pytest
from pytest_mock import MockFixture

from speech_prep.core import SoundFile
from speech_prep.exceptions import SpeechPrepError


@pytest.mark.unit
class TestSoundFileInit:
    """Test the initialization of SoundFile objects."""

    def test_init_file_not_found(self) -> None:
        """Test initialization with a non-existent file."""
        with pytest.raises(FileNotFoundError):
            SoundFile(Path("/non/existent/file.wav"))

    def test_init_metadata_extraction_error(
        self, mocker: MockFixture, temp_dir: Path
    ) -> None:
        """Test handling of metadata extraction errors."""
        # Create an empty file
        test_file = temp_dir / "empty.wav"
        test_file.touch()

        # Mock get_audio_properties to raise an exception
        mocker.patch(
            "speech_prep.core.get_audio_properties",
            side_effect=Exception("Metadata extraction failed"),
        )

        with pytest.raises(SpeechPrepError) as exc_info:
            SoundFile(test_file)

        assert "Failed to extract metadata" in str(exc_info.value)

    def test_init_silence_detection_error(
        self, mocker: MockFixture, audio_file_with_silence: tuple[Path, float]
    ) -> None:
        """Test handling of silence detection errors."""
        file_path, _ = audio_file_with_silence

        # Mock detect_silence to raise an exception
        mocker.patch(
            "speech_prep.core.detect_silence",
            side_effect=Exception("Silence detection failed"),
        )

        # Mock get_audio_properties to return test values
        mocker.patch(
            "speech_prep.core.get_audio_properties",
            return_value=(5.0, 10000, "wav"),
        )

        # Should not raise an exception, but should set silence_periods to empty list
        sound_file = SoundFile(file_path)
        assert sound_file.silence_periods == []
        assert sound_file.median_silence == 0.0


@pytest.mark.unit
class TestSoundFileEquality:
    """Test the equality comparison of SoundFile objects."""

    def test_equality_same_path(
        self, mocker: MockFixture, audio_file_with_silence: tuple[Path, float]
    ) -> None:
        """Test that two SoundFile objects with the same path are equal."""
        file_path, _ = audio_file_with_silence

        # Mock dependencies to ensure consistent behavior
        mocker.patch(
            "speech_prep.core.get_audio_properties",
            return_value=(5.0, 10000, "wav"),
        )
        mocker.patch(
            "speech_prep.core.detect_silence",
            return_value=[],
        )

        sound_file1 = SoundFile(file_path)
        sound_file2 = SoundFile(file_path)

        assert sound_file1 == sound_file2

    def test_equality_different_path(self, mocker: MockFixture, temp_dir: Path) -> None:
        """Test that two SoundFile objects with different paths are not equal."""
        # Create two different files
        file1 = temp_dir / "file1.wav"
        file2 = temp_dir / "file2.wav"
        file1.touch()
        file2.touch()

        # Mock dependencies to ensure consistent behavior
        mocker.patch(
            "speech_prep.core.get_audio_properties",
            return_value=(5.0, 10000, "wav"),
        )
        mocker.patch(
            "speech_prep.core.detect_silence",
            return_value=[],
        )

        sound_file1 = SoundFile(file1)
        sound_file2 = SoundFile(file2)

        assert sound_file1 != sound_file2

    def test_equality_non_soundfile(
        self, mocker: MockFixture, audio_file_with_silence: tuple[Path, float]
    ) -> None:
        """Test that a SoundFile compared to a non-SoundFile object returns False."""
        file_path, _ = audio_file_with_silence

        # Mock dependencies to ensure consistent behavior
        mocker.patch(
            "speech_prep.core.get_audio_properties",
            return_value=(5.0, 10000, "wav"),
        )
        mocker.patch(
            "speech_prep.core.detect_silence",
            return_value=[],
        )

        sound_file = SoundFile(file_path)

        assert sound_file != "not a SoundFile"
        assert sound_file != 123
        assert sound_file is not None


@pytest.mark.unit
class TestSoundFileStringRepresentation:
    """Test the string representation of SoundFile objects."""

    def test_str_basic_info(
        self, mocker: MockFixture, audio_file_with_silence: tuple[Path, float]
    ) -> None:
        """Test that the string representation includes basic audio information."""
        file_path, duration = audio_file_with_silence

        # Mock dependencies to return consistent values
        mocker.patch(
            "speech_prep.core.get_audio_properties",
            return_value=(duration, 10000, "wav"),
        )
        mocker.patch(
            "speech_prep.core.detect_silence",
            return_value=[],
        )

        sound_file = SoundFile(file_path)
        str_repr = str(sound_file)

        # Check basic info presence
        assert f"SoundFile: {file_path}" in str_repr
        assert f"Duration: {duration:.2f} seconds" in str_repr
        assert "Format: wav" in str_repr
        assert "File size: " in str_repr
        assert "Silence periods: 0 detected" in str_repr
        assert "Median silence: 0.00 seconds" in str_repr

    def test_str_no_silence_periods(
        self, mocker: MockFixture, audio_file_no_silence: tuple[Path, float]
    ) -> None:
        """Test string representation when no silence periods are detected."""
        file_path, duration = audio_file_no_silence

        # Mock dependencies
        mocker.patch(
            "speech_prep.core.get_audio_properties",
            return_value=(duration, 10000, "wav"),
        )
        mocker.patch(
            "speech_prep.core.detect_silence",
            return_value=[],
        )

        sound_file = SoundFile(file_path)
        str_repr = str(sound_file)

        assert "Silence periods: 0 detected" in str_repr
        assert "None detected" in str_repr

    def test_str_few_silence_periods(
        self, mocker: MockFixture, audio_file_with_silence: tuple[Path, float]
    ) -> None:
        """Test string representation with few silence periods (≤ 6)."""
        file_path, duration = audio_file_with_silence

        # Define a few silence periods: 2 periods
        silence_periods = [
            (1.0, 2.0, 1.0),  # (start, end, duration)
            (3.0, 4.0, 1.0),
        ]

        # Mock dependencies
        mocker.patch(
            "speech_prep.core.get_audio_properties",
            return_value=(duration, 10000, "wav"),
        )
        mocker.patch(
            "speech_prep.core.detect_silence",
            return_value=silence_periods,
        )
        mocker.patch(
            "speech_prep.core.calculate_median_silence",
            return_value=1.0,
        )

        sound_file = SoundFile(file_path)
        str_repr = str(sound_file)

        # Verify all silence periods are listed (no ellipsis)
        assert "1: 1.00s - 2.00s (1.00s)" in str_repr
        assert "2: 3.00s - 4.00s (1.00s)" in str_repr
        assert "..." not in str_repr

    def test_str_many_silence_periods(
        self, mocker: MockFixture, audio_file_with_silence: tuple[Path, float]
    ) -> None:
        """Test string representation with many silence periods (> 6)."""
        file_path, duration = audio_file_with_silence

        # Define many silence periods: 10 periods
        silence_periods = [(i * 0.5, i * 0.5 + 0.2, 0.2) for i in range(10)]

        # Mock dependencies
        mocker.patch(
            "speech_prep.core.get_audio_properties",
            return_value=(duration, 10000, "wav"),
        )
        mocker.patch(
            "speech_prep.core.detect_silence",
            return_value=silence_periods,
        )
        mocker.patch(
            "speech_prep.core.calculate_median_silence",
            return_value=0.2,
        )

        sound_file = SoundFile(file_path)
        str_repr = str(sound_file)

        # Verify first 3 and last 3 silence periods are listed with ellipsis
        assert "1: 0.00s - 0.20s (0.20s)" in str_repr
        assert "2: 0.50s - 0.70s (0.20s)" in str_repr
        assert "3: 1.00s - 1.20s (0.20s)" in str_repr
        assert "... 4 more periods ..." in str_repr
        assert "8: 3.50s - 3.70s (0.20s)" in str_repr
        assert "9: 4.00s - 4.20s (0.20s)" in str_repr
        assert "10: 4.50s - 4.70s (0.20s)" in str_repr


@pytest.mark.unit
class TestSoundFileStrip:
    """Test the silence stripping functionality."""

    def test_strip_success(
        self,
        mocker: MockFixture,
        audio_file_with_silence: tuple[Path, float],
        temp_dir: Path,
    ) -> None:
        """Test successful silence stripping."""
        input_path, duration = audio_file_with_silence
        output_path = temp_dir / "stripped.wav"

        # Define silence periods
        silence_periods = [
            (1.0, 2.0, 1.0),  # (start, end, duration)
            (3.0, 4.0, 1.0),
        ]

        # Mock dependencies for the input file
        mocker.patch(
            "speech_prep.core.get_audio_properties",
            side_effect=[(duration, 10000, "wav"), (3.0, 8000, "wav")],
        )
        mocker.patch(
            "speech_prep.core.detect_silence",
            side_effect=[silence_periods, []],
        )
        mocker.patch(
            "speech_prep.core.calculate_median_silence",
            return_value=1.0,
        )

        # Mock the strip_silence function and make it create the output file
        def side_effect_create_file(*args, **kwargs):
            # Create the output file so it exists
            output_path.touch()

        mock_strip = mocker.patch(
            "speech_prep.core.strip_silence", side_effect=side_effect_create_file
        )

        # Create the original SoundFile
        sound_file = SoundFile(input_path)

        # Call strip method
        result = sound_file.strip(output_path)

        # Verify strip_silence was called with correct arguments
        mock_strip.assert_called_once_with(
            input_path, output_path, silence_periods, duration, True, True
        )

        # Verify a new SoundFile instance was returned
        assert result is not None
        assert result != sound_file
        assert result.path == output_path

    def test_strip_no_silence(
        self,
        mocker: MockFixture,
        audio_file_no_silence: tuple[Path, float],
        temp_dir: Path,
    ) -> None:
        """Test strip when no silence is detected."""
        input_path, duration = audio_file_no_silence
        output_path = temp_dir / "stripped.wav"

        # Mock dependencies
        mocker.patch(
            "speech_prep.core.get_audio_properties",
            return_value=(duration, 10000, "wav"),
        )
        mocker.patch(
            "speech_prep.core.detect_silence",
            return_value=[],
        )

        # Create the SoundFile
        sound_file = SoundFile(input_path)

        # Call strip method
        result = sound_file.strip(output_path)

        # Verify original object is returned (no processing needed)
        assert result == sound_file

    def test_strip_error(
        self,
        mocker: MockFixture,
        audio_file_with_silence: tuple[Path, float],
        temp_dir: Path,
    ) -> None:
        """Test handling of errors during strip operation."""
        input_path, duration = audio_file_with_silence
        output_path = temp_dir / "stripped.wav"

        # Define silence periods
        silence_periods = [
            (1.0, 2.0, 1.0),
            (3.0, 4.0, 1.0),
        ]

        # Mock dependencies
        mocker.patch(
            "speech_prep.core.get_audio_properties",
            return_value=(duration, 10000, "wav"),
        )
        mocker.patch(
            "speech_prep.core.detect_silence",
            return_value=silence_periods,
        )
        mocker.patch(
            "speech_prep.core.calculate_median_silence",
            return_value=1.0,
        )

        # Mock strip_silence to raise an exception
        mocker.patch(
            "speech_prep.core.strip_silence",
            side_effect=SpeechPrepError("Stripping failed"),
        )

        # Mock the logger to check it's called
        mock_logger = mocker.patch("speech_prep.core.logger")

        # Create the SoundFile
        sound_file = SoundFile(input_path)

        # Call strip method
        result = sound_file.strip(output_path)

        # Verify error is logged and None is returned
        mock_logger.error.assert_called_once()
        assert "Error during strip" in mock_logger.error.call_args[0][0]
        assert result is None


@pytest.mark.unit
class TestSoundFileConvert:
    """Test the format conversion functionality."""

    def test_convert_success(
        self,
        mocker: MockFixture,
        audio_file_with_silence: tuple[Path, float],
        temp_dir: Path,
    ) -> None:
        """Test successful format conversion."""
        input_path, duration = audio_file_with_silence
        output_path = temp_dir / "converted.mp3"

        # Mock dependencies for the input file
        mocker.patch(
            "speech_prep.core.get_audio_properties",
            side_effect=[(duration, 10000, "wav"), (duration, 8000, "mp3")],
        )
        mocker.patch(
            "speech_prep.core.detect_silence",
            side_effect=[[], []],
        )

        # Mock the convert_format function and make it create the output file
        def side_effect_create_file(*args, **kwargs):
            # Create the output file so it exists
            output_path.touch()

        mock_convert = mocker.patch(
            "speech_prep.core.convert_format", side_effect=side_effect_create_file
        )

        # Create the original SoundFile
        sound_file = SoundFile(input_path)

        # Import AudioFormat
        from speech_prep.formats import AudioFormat

        # Call convert method
        result = sound_file.convert(output_path, AudioFormat.MP3, audio_bitrate="192k")

        # Verify convert_format was called with correct arguments
        mock_convert.assert_called_once_with(
            input_path, output_path, AudioFormat.MP3, "192k"
        )

        # Verify a new SoundFile instance was returned
        assert result is not None
        assert result != sound_file
        assert result.path == output_path

    def test_convert_error(
        self,
        mocker: MockFixture,
        audio_file_with_silence: tuple[Path, float],
        temp_dir: Path,
    ) -> None:
        """Test handling of errors during conversion."""
        input_path, duration = audio_file_with_silence
        output_path = temp_dir / "converted.mp3"

        # Mock dependencies
        mocker.patch(
            "speech_prep.core.get_audio_properties",
            return_value=(duration, 10000, "wav"),
        )
        mocker.patch(
            "speech_prep.core.detect_silence",
            return_value=[],
        )

        # Mock convert_format to raise an exception
        mocker.patch(
            "speech_prep.core.convert_format",
            side_effect=SpeechPrepError("Conversion failed"),
        )

        # Mock the logger to check it's called
        mock_logger = mocker.patch("speech_prep.core.logger")

        # Create the SoundFile
        sound_file = SoundFile(input_path)

        # Import AudioFormat
        from speech_prep.formats import AudioFormat

        # Call convert method
        result = sound_file.convert(output_path, AudioFormat.MP3)

        # Verify error is logged and None is returned
        mock_logger.error.assert_called_once()
        assert "Error during convert" in mock_logger.error.call_args[0][0]
        assert result is None


@pytest.mark.unit
class TestSoundFileSpeed:
    """Test the speed adjustment functionality."""

    def test_speed_success(
        self,
        mocker: MockFixture,
        audio_file_with_silence: tuple[Path, float],
        temp_dir: Path,
    ) -> None:
        """Test successful speed adjustment."""
        input_path, duration = audio_file_with_silence
        output_path = temp_dir / "speed_adjusted.wav"
        speed_factor = 2.0

        # Mock dependencies for the input and output files
        mocker.patch(
            "speech_prep.core.get_audio_properties",
            side_effect=[
                (duration, 10000, "wav"),
                (duration / speed_factor, 8000, "wav"),
            ],
        )
        mocker.patch(
            "speech_prep.core.detect_silence",
            side_effect=[[], []],
        )

        # Mock the adjust_speed function and make it create the output file
        def side_effect_create_file(*args, **kwargs):
            # Create the output file so it exists
            output_path.touch()

        mock_speed = mocker.patch(
            "speech_prep.core.adjust_speed", side_effect=side_effect_create_file
        )

        # Create the original SoundFile
        sound_file = SoundFile(input_path, min_silence_duration=1.0)

        # Call speed method
        result = sound_file.speed(output_path, speed_factor)

        # Verify adjust_speed was called with correct arguments
        mock_speed.assert_called_once_with(input_path, output_path, speed_factor)

        # Verify a new SoundFile instance was returned with adjusted silence threshold
        assert result is not None
        assert result != sound_file
        assert result.path == output_path
        assert result.min_silence_duration == (
            sound_file.min_silence_duration / speed_factor
        )

    def test_speed_error(
        self,
        mocker: MockFixture,
        audio_file_with_silence: tuple[Path, float],
        temp_dir: Path,
    ) -> None:
        """Test handling of errors during speed adjustment."""
        input_path, duration = audio_file_with_silence
        output_path = temp_dir / "speed_adjusted.wav"
        speed_factor = 2.0

        # Mock dependencies
        mocker.patch(
            "speech_prep.core.get_audio_properties",
            return_value=(duration, 10000, "wav"),
        )
        mocker.patch(
            "speech_prep.core.detect_silence",
            return_value=[],
        )

        # Mock adjust_speed to raise an exception
        mocker.patch(
            "speech_prep.core.adjust_speed",
            side_effect=SpeechPrepError("Speed adjustment failed"),
        )

        # Mock the logger to check it's called
        mock_logger = mocker.patch("speech_prep.core.logger")

        # Create the SoundFile
        sound_file = SoundFile(input_path)

        # Call speed method
        result = sound_file.speed(output_path, speed_factor)

        # Verify error is logged and None is returned
        mock_logger.error.assert_called_once()
        assert "Error during speed" in mock_logger.error.call_args[0][0]
        assert result is None


@pytest.mark.integration
class TestSoundFileIntegration:
    """Integration tests for SoundFile class."""

    def test_processing_pipeline(
        self,
        mocker: MockFixture,
        audio_file_with_silence: tuple[Path, float],
        temp_dir: Path,
    ) -> None:
        """Test a complete processing pipeline (strip -> speed -> convert)."""
        input_path, _ = audio_file_with_silence

        # Define paths for intermediate and final outputs
        stripped_path = temp_dir / "stripped.wav"
        sped_path = temp_dir / "sped.wav"
        converted_path = temp_dir / "final.mp3"

        # Mock all processing functions to create their output files
        def mock_process_file(*args, **kwargs):
            # Extract the output path (should be the second argument)
            output_path = args[1]
            # Create the output file
            Path(output_path).touch()

        mocker.patch("speech_prep.core.strip_silence", side_effect=mock_process_file)
        mocker.patch("speech_prep.core.adjust_speed", side_effect=mock_process_file)
        mocker.patch("speech_prep.core.convert_format", side_effect=mock_process_file)

        # Mock get_audio_properties to return different values for different files
        def mock_get_properties(file_path):
            if str(file_path).endswith("stripped.wav"):
                return 3.0, 8000, "wav"
            elif str(file_path).endswith("sped.wav"):
                return 2.0, 7000, "wav"
            elif str(file_path).endswith("final.mp3"):
                return 2.0, 6000, "mp3"
            else:
                return 5.0, 10000, "wav"

        mocker.patch(
            "speech_prep.core.get_audio_properties", side_effect=mock_get_properties
        )

        # Mock silence detection
        mocker.patch(
            "speech_prep.core.detect_silence",
            return_value=[(1.0, 2.0, 1.0), (3.0, 4.0, 1.0)],
        )
        mocker.patch(
            "speech_prep.core.calculate_median_silence",
            return_value=1.0,
        )

        # Create a SoundFile instance
        sound_file = SoundFile(input_path)

        # Execute the pipeline
        stripped = sound_file.strip(stripped_path)
        assert stripped is not None, "Strip operation failed"

        sped = stripped.speed(sped_path, 1.5)
        assert sped is not None, "Speed operation failed"

        # Import AudioFormat
        from speech_prep.formats import AudioFormat

        converted = sped.convert(converted_path, AudioFormat.MP3, audio_bitrate="192k")
        assert converted is not None, "Convert operation failed"

        # Verify the final file exists and has expected properties
        assert converted.path.exists()
        assert converted.format == "mp3"  # Should be the converted format
