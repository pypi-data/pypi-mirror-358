"""Audio processing operations for speech preparation."""

from pathlib import Path
import subprocess
from typing import Optional

from .exceptions import FFmpegError
from .formats import AudioFormat


def strip_silence(
    input_path: Path,
    output_path: Path,
    silence_periods: list[tuple[float, float, float]],
    total_duration: float,
    leading: bool = True,
    trailing: bool = True,
) -> None:
    """
    Create a new audio file with leading and/or trailing silence removed.

    Args:
        input_path: Path to the input audio file
        output_path: Path to save the new file
        silence_periods: List of silence periods as (start, end, duration) tuples
        total_duration: Total duration of the audio file
        leading: Whether to remove leading silence
        trailing: Whether to remove trailing silence

    Raises:
        FFmpegError: If the ffmpeg operation fails
    """
    if not silence_periods:
        raise FFmpegError("No silence periods detected, nothing to strip")

    # Determine start and end times based on silence periods
    start_time = 0.0
    end_time = total_duration

    if leading and silence_periods[0][0] == 0:
        # First silence period starts at 0, so it's leading silence
        start_time = silence_periods[0][1]

    if trailing:
        last_silence = silence_periods[-1]
        # Check if the last silence extends to the end of the file
        # Allow a small buffer (0.1s) for rounding errors
        if abs(last_silence[1] - total_duration) < 0.1:
            end_time = last_silence[0]

    # Use ffmpeg to cut the file
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output file if it exists
        "-i",
        str(input_path),
        "-ss",
        str(start_time),  # Start time
        "-to",
        str(end_time),  # End time
        "-c",
        "copy",  # Copy streams without re-encoding
        str(output_path),
    ]

    print(f"Stripping silence: {start_time:.2f}s to {end_time:.2f}s")
    _run_ffmpeg_command(cmd, "stripping silence")


def convert_format(
    input_path: Path,
    output_path: Path,
    target_format: AudioFormat,
    audio_bitrate: Optional[str] = None,
) -> None:
    """
    Convert the audio file to a different format.

    Args:
        input_path: Path to the input audio file
        output_path: Path to save the converted file
        target_format: Target audio format
        audio_bitrate: Optional bitrate for the output file (e.g., '192k', '320k')

    Raises:
        FFmpegError: If the ffmpeg operation fails
    """
    # Build ffmpeg command
    cmd = ["ffmpeg", "-y", "-i", str(input_path)]

    # Add bitrate if specified
    if audio_bitrate:
        cmd.extend(["-b:a", audio_bitrate])

    # Add output file
    cmd.append(str(output_path))

    # Determine the input format from the file extension
    input_format = AudioFormat.UNKNOWN
    try:
        ext = input_path.suffix.lower().lstrip(".")
        input_format = AudioFormat(ext)
    except ValueError:
        pass  # Keep as UNKNOWN if not found

    # Use the provided target_format
    output_format = target_format

    print(
        f"Converting {input_path.name} from "
        f"{input_format.value} to {output_format.value}"
    )

    _run_ffmpeg_command(cmd, "converting format")


def adjust_speed(input_path: Path, output_path: Path, speed_factor: float) -> None:
    """
    Create a new audio file with adjusted playback speed.

    Args:
        input_path: Path to the input audio file
        output_path: Path to save the speed-adjusted file
        speed_factor: Speed multiplier (e.g., 2.0 for 2x speed, 0.5 for half speed)

    Raises:
        FFmpegError: If the ffmpeg operation fails or speed_factor is invalid
    """
    if speed_factor <= 0:
        raise FFmpegError("Speed factor must be positive")

    # Use ffmpeg's atempo filter for speed adjustment
    # Note: atempo filter is limited to 0.5x to 2.0x range
    # For factors outside this range, we need to chain multiple atempo filters

    atempo_filters = []
    remaining_factor = speed_factor

    # Split into multiple atempo filters if needed
    while remaining_factor > 2.0:
        atempo_filters.append("atempo=2.0")
        remaining_factor /= 2.0

    while remaining_factor < 0.5:
        atempo_filters.append("atempo=0.5")
        remaining_factor /= 0.5

    # Add the final adjustment
    if abs(remaining_factor - 1.0) > 0.01:  # If not very close to 1.0
        atempo_filters.append(f"atempo={remaining_factor}")

    # Build the filter string
    filter_str = ",".join(atempo_filters) if atempo_filters else "atempo=1.0"

    # Determine appropriate codec based on output format
    output_format = AudioFormat.UNKNOWN
    try:
        ext = output_path.suffix.lower().lstrip(".")
        output_format = AudioFormat(ext)
    except ValueError:
        pass  # Keep as UNKNOWN

    if output_format == AudioFormat.MP3:
        codec = "libmp3lame"
    elif output_format == AudioFormat.WAV:
        codec = "pcm_s16le"
    else:
        codec = "libmp3lame"  # Default to mp3 codec

    # Build ffmpeg command
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-filter:a",
        filter_str,
        "-c:a",
        codec,
        str(output_path),
    ]

    print(f"Adjusting speed by factor {speed_factor}x using filter: {filter_str}")
    _run_ffmpeg_command(cmd, "adjusting speed")


def _run_ffmpeg_command(cmd: list[str], operation_name: str) -> None:
    """
    Run an ffmpeg command with error handling.

    Args:
        cmd: List of command arguments
        operation_name: Description of the operation for error messages

    Raises:
        FFmpegError: If ffmpeg command fails
    """
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        raise FFmpegError(
            f"Error during {operation_name}", stderr=e.stderr, returncode=e.returncode
        ) from e
    except FileNotFoundError as e:
        raise FFmpegError(
            f"ffmpeg not found during {operation_name}. "
            "Please ensure ffmpeg is installed and accessible."
        ) from e
