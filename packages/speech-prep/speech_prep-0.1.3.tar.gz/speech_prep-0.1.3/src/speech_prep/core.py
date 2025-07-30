"""Core SoundFile class for audio file manipulation."""

import logging
from pathlib import Path
from typing import Optional

from .detection import calculate_median_silence, detect_silence
from .exceptions import SpeechPrepError
from .processing import adjust_speed, convert_format, strip_silence
from .utils import format_time, get_audio_properties

# Configure package logger
logger = logging.getLogger("speech_prep")
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)


class SoundFile:
    """Represents an audio file with silence detection and processing capabilities."""

    def __init__(
        self,
        path: Path,
        noise_threshold_db: int = -30,
        min_silence_duration: float = 0.5,
    ):
        """
        Initialize a SoundFile object.

        Args:
            path: Path to the audio file
            noise_threshold_db: Threshold (in dB) for silence detection
            min_silence_duration: Minimum duration (in seconds) to consider as silence
        """
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"Audio file not found: {self.path}")

        try:
            self.duration, self.file_size, self.format = get_audio_properties(self.path)
        except Exception as e:
            raise SpeechPrepError(f"Failed to extract metadata: {e}") from e

        try:
            self.silence_periods = detect_silence(
                self.path,
                noise_threshold_db=noise_threshold_db,
                min_silence_duration=min_silence_duration,
            )
        except Exception:
            self.silence_periods = []

        if self.silence_periods:
            self.median_silence = calculate_median_silence(self.silence_periods)
        else:
            self.median_silence = 0.0

        self.noise_threshold_db = noise_threshold_db
        self.min_silence_duration = min_silence_duration

    def __eq__(self, other: object) -> bool:
        """Two files are equal if they reference the same path."""
        if not isinstance(other, SoundFile):
            return False
        return self.path == other.path

    def __str__(self) -> str:
        """
        Return a string representation of the SoundFile object.

        Displays a summary of audio properties and the first/last three silence periods.
        """
        # Format basic audio information
        basic_info = [
            f"SoundFile: {self.path}",
            f"  Duration: {self.duration:.2f} seconds ({format_time(self.duration)})",
            f"  Format: {self.format}",
            f"  File size: {self.file_size / 1024 / 1024:.2f} MB",
            f"  Silence periods: {len(self.silence_periods)} detected",
            f"  Median silence: {self.median_silence:.2f} seconds",
        ]

        # Format silence periods (first 3, ellipsis, last 3)
        silence_info = ["  Silence periods:"]
        if self.silence_periods:
            # Always show at least the first and last if there are any
            total_periods = len(self.silence_periods)

            # Determine how many to show at start and end
            to_show = min(3, total_periods)

            # Add the first 'to_show' periods
            for i in range(to_show):
                start, end, duration = self.silence_periods[i]
                silence_info.append(
                    f"    {i + 1}: {start:.2f}s - {end:.2f}s ({duration:.2f}s) "
                    f"[{format_time(start)} - {format_time(end)}]"
                )

            # Add ellipsis if there are more than 2*to_show periods
            if total_periods > 2 * to_show:
                silence_info.append(
                    f"    ... {total_periods - 2 * to_show} more periods ..."
                )

            # Add the last 'to_show' periods if there are more than 'to_show' total
            if total_periods > to_show:
                for i in range(max(to_show, total_periods - to_show), total_periods):
                    start, end, duration = self.silence_periods[i]
                    silence_info.append(
                        f"    {i + 1}: {start:.2f}s - {end:.2f}s ({duration:.2f}s) "
                        f"[{format_time(start)} - {format_time(end)}]"
                    )
        else:
            silence_info.append("    None detected")

        # Combine all information
        return "\n".join(basic_info + silence_info)

    # __new__ removed; all initialization is handled in __init__

    def strip(
        self, output_path: Path, leading: bool = True, trailing: bool = True
    ) -> Optional["SoundFile"]:
        """
        Create a new audio file with leading and/or trailing silence removed.

        Args:
            output_path: Path to save the new file.
            leading: Whether to remove leading silence
            trailing: Whether to remove trailing silence
        Returns:
            A new SoundFile instance for the created file, or None if operation failed
        """
        if not self.silence_periods:
            logger.info(
                f"No silence periods detected in {self.path}, nothing to strip."
            )
            return self
        try:
            strip_silence(
                self.path,
                output_path,
                self.silence_periods,
                self.duration,
                leading,
                trailing,
            )
            return SoundFile(
                output_path, self.noise_threshold_db, self.min_silence_duration
            )
        except SpeechPrepError as e:
            logger.error(f"Error during strip: {e}")
            return None

    def convert(
        self, output_path: Path, audio_bitrate: Optional[str] = None
    ) -> Optional["SoundFile"]:
        """
        Convert the audio file to a different format.

        Args:
            output_path: Path to save the converted file
            audio_bitrate: Optional bitrate for the output file (e.g., '192k', '320k')

        Returns:
            A new SoundFile instance for the converted file, or None if operation failed
        """
        try:
            convert_format(self.path, output_path, audio_bitrate)
            return SoundFile(
                output_path, self.noise_threshold_db, self.min_silence_duration
            )
        except SpeechPrepError as e:
            logger.error(f"Error during convert: {e}")
            return None

    def speed(self, output_path: Path, speed_factor: float) -> Optional["SoundFile"]:
        """
        Create a new audio file with adjusted playback speed.

        Args:
            output_path: Path to save the new file.
            speed_factor: Speed multiplier (e.g., 2.0 for 2x speed, 0.5 for half speed)

        Returns:
            A new SoundFile instance for the created file, or None if operation failed
        """
        try:
            adjust_speed(self.path, output_path, speed_factor)
            # Adjust silence threshold for the new file
            adjusted_threshold = self.min_silence_duration / speed_factor
            logger.info(
                f"Silence threshold: {adjusted_threshold:.2f}s for sped-up file"
            )
            return SoundFile(output_path, self.noise_threshold_db, adjusted_threshold)
        except SpeechPrepError as e:
            logger.error(f"Error during speed: {e}")
            return None
