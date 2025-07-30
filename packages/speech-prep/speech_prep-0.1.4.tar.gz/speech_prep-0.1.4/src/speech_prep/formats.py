"""Enums for audio file formats."""

from enum import Enum


class AudioFormat(Enum):
    """Enum representing supported audio formats."""

    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    UNKNOWN = "unknown"
