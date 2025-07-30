"""
Speech Prep - Audio preprocessing toolkit for speech-to-text applications.

This package provides tools to prepare audio files for speech-to-text processing,
including silence detection and removal, speed adjustment, and format conversion.
"""

from .core import SoundFile
from .exceptions import (
    AudioPropertiesError,
    FFmpegError,
    FileValidationError,
    SilenceDetectionError,
    SpeechPrepError,
)
from .formats import AudioFormat

# Import version from hatch-vcs
try:
    from importlib.metadata import version as get_metadata_version

    __version__ = get_metadata_version("speech-prep")
except ImportError:
    # Development or not installed
    __version__ = "0.0.0"

__all__ = [
    "SoundFile",
    "AudioFormat",
    "SpeechPrepError",
    "FFmpegError",
    "FileValidationError",
    "AudioPropertiesError",
    "SilenceDetectionError",
    "__version__",
]
