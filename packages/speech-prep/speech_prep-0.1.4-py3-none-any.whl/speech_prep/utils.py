"""Utility functions for audio file operations."""

import json
from pathlib import Path
import subprocess

from .exceptions import AudioPropertiesError, FileValidationError
from .formats import AudioFormat


def validate_file(file_path: Path) -> bool:
    """
    Validate that the file exists and is a regular file.

    Args:
        file_path: Path to the file to validate

    Returns:
        True if file is valid

    Raises:
        FileValidationError: If file doesn't exist or is not a regular file
    """
    if not file_path.exists():
        raise FileValidationError(f"File {file_path} does not exist")

    if not file_path.is_file():
        raise FileValidationError(f"Path {file_path} is not a regular file")

    return True


def get_audio_properties(file_path: Path) -> tuple[float, int, AudioFormat]:
    """
    Extract audio properties (duration, file size, format) using ffprobe.

    Args:
        file_path: Path to the audio file

    Returns:
        Tuple of (duration, file_size, audio_format) where audio_format
        is an AudioFormat enum representing the detected audio format

    Raises:
        AudioPropertiesError: If properties cannot be extracted
    """
    probe_cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration,size,format_name",
        "-of",
        "json",
        str(file_path),
    ]

    try:
        probe_result = subprocess.run(
            probe_cmd,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise AudioPropertiesError(f"Error probing file {file_path}: {e.stderr}") from e
    except FileNotFoundError as e:
        raise AudioPropertiesError(
            "ffprobe not found. Please ensure ffmpeg is installed and accessible."
        ) from e

    try:
        probe_data = json.loads(probe_result.stdout)["format"]
        duration = float(probe_data["duration"])
        file_size = int(probe_data["size"])
        format_str = probe_data["format_name"].split(",")[
            0
        ]  # Get the first format name

        # Convert format string to enum
        try:
            audio_format = AudioFormat(format_str.lower())
        except ValueError:
            # If not a direct match, use UNKNOWN
            audio_format = AudioFormat.UNKNOWN

        if duration <= 0 or file_size <= 0:
            raise AudioPropertiesError(
                f"Invalid duration or file size for {file_path}. "
                f"Duration: {duration}, Size: {file_size}"
            )

        return duration, file_size, audio_format

    except (KeyError, ValueError, json.JSONDecodeError) as e:
        raise AudioPropertiesError(f"Error parsing probe data: {e}") from e


def format_time(seconds: float) -> str:
    """
    Format seconds as HH:MM:SS.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string
    """
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds_int = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds_int:02}"


def run_ffmpeg_command(
    cmd: list[str], operation_name: str
) -> subprocess.CompletedProcess[str]:
    """
    Run an ffmpeg command with error handling.

    Args:
        cmd: List of command arguments
        operation_name: Description of the operation for error messages

    Returns:
        CompletedProcess result

    Raises:
        AudioPropertiesError: If ffmpeg command fails
    """
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result

    except subprocess.CalledProcessError as e:
        raise AudioPropertiesError(f"Error during {operation_name}: {e.stderr}") from e
    except FileNotFoundError as e:
        raise AudioPropertiesError(
            "ffmpeg not found. Please ensure ffmpeg is installed and accessible."
        ) from e
