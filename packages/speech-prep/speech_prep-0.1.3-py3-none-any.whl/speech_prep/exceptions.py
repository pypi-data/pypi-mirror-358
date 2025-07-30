"""Custom exceptions for the speech-prep package."""

from typing import Optional


class SpeechPrepError(Exception):
    """Base exception for all speech-prep related errors."""

    pass


class FFmpegError(SpeechPrepError):
    """Raised when ffmpeg command fails or returns an error."""

    def __init__(
        self,
        message: str,
        stderr: Optional[str] = None,
        returncode: Optional[int] = None,
    ):
        """
        Initialize FFmpegError with error details.

        Args:
            message: Error message
            stderr: Standard error output from ffmpeg
            returncode: Return code from ffmpeg process
        """
        self.stderr = stderr
        self.returncode = returncode
        super().__init__(message)


class FileValidationError(SpeechPrepError):
    """Raised when file validation fails."""

    pass


class AudioPropertiesError(SpeechPrepError):
    """Raised when audio properties cannot be extracted."""

    pass


class SilenceDetectionError(SpeechPrepError):
    """Raised when silence detection fails."""

    pass
