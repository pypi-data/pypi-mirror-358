"""Silence detection functionality for audio files."""

from pathlib import Path
import re
import subprocess
from typing import Optional

from .exceptions import SilenceDetectionError


def detect_silence(
    file_path: Path, noise_threshold_db: int, min_silence_duration: float
) -> list[tuple[float, float, float]]:
    """
    Detect silence periods using ffmpeg silencedetect filter.

    Args:
        file_path: Path to the audio file
        noise_threshold_db: Threshold (in dB) for silence detection
        min_silence_duration: Minimum duration (in seconds) to consider as silence

    Returns:
        List of silence periods as (start, end, duration) tuples

    Raises:
        SilenceDetectionError: If silence detection fails
    """
    silence_cmd = [
        "ffmpeg",
        "-i",
        str(file_path),
        "-af",
        f"silencedetect=noise={noise_threshold_db}dB:d={min_silence_duration}",
        "-f",
        "null",
        "-",
    ]

    try:
        silence_proc = subprocess.run(
            silence_cmd,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise SilenceDetectionError(
            f"Error detecting silence in file {file_path}: {e.stderr}"
        ) from e
    except FileNotFoundError as e:
        raise SilenceDetectionError(
            "ffmpeg not found. Please ensure ffmpeg is installed and accessible."
        ) from e

    return parse_silence_output(silence_proc.stderr)


def parse_silence_output(silence_output: str) -> list[tuple[float, float, float]]:
    """
    Parse the ffmpeg silence detection output to extract silence periods.

    Args:
        silence_output: stderr output from ffmpeg silence detection

    Returns:
        List of silence periods as (start, end, duration) tuples
    """
    silence_periods = []
    start_time: Optional[float] = None

    for line in silence_output.splitlines():
        if "silence_start" in line:
            # Extract the start time
            match = re.search(r"silence_start: (\d+(?:\.\d+)?)", line)
            if match:
                start_time = float(match.group(1))
        elif "silence_end" in line and start_time is not None:
            # Extract the end time and duration
            match = re.search(
                r"silence_end: (\d+(?:\.\d+)?) \| silence_duration: (\d+(?:\.\d+)?)",
                line,
            )
            if match:
                end_time = float(match.group(1))
                silence_duration = float(match.group(2))
                silence_periods.append((start_time, end_time, silence_duration))
                start_time = None

    return silence_periods


def calculate_median_silence(
    silence_periods: list[tuple[float, float, float]],
) -> float:
    """
    Calculate the median duration of silence periods.

    Args:
        silence_periods: List of silence periods as (start, end, duration) tuples

    Returns:
        Median silence duration in seconds
    """
    if not silence_periods:
        return 0.0

    silence_durations = [duration for _, _, duration in silence_periods]
    silence_durations.sort()

    n = len(silence_durations)
    if n % 2 == 0:
        # Even number of elements - take average of middle two
        return (silence_durations[n // 2 - 1] + silence_durations[n // 2]) / 2
    else:
        # Odd number of elements - take middle element
        return silence_durations[n // 2]
