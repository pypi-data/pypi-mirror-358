# Speech Prep

Audio preprocessing toolkit for speech-to-text applications using FFmpeg.

## Overview

Speech Prep is a Python package designed to prepare audio files for speech-to-text processing. It provides tools for silence detection and removal, speed adjustment, and format conversion - all essential steps for optimizing audio before transcription.

## Features

- **Silence Detection**: Automatically detect silence periods in audio files
- **Silence Removal**: Remove leading/trailing silence to clean up recordings
- **Speed Adjustment**: Change playback speed while maintaining audio quality
- **Format Conversion**: Convert between different audio formats (MP3, WAV, FLAC, etc.)
- **Clean API**: Simple, intuitive interface with method chaining support
- **FFmpeg Integration**: Leverages the power and reliability of FFmpeg

## Requirements

- Python 3.9+
- FFmpeg (must be installed and accessible via PATH)

## Installation

```bash
# Install from PyPI (when published)
pip install speech-prep

# Or install from source
git clone https://github.com/dimdasci/speech-prep.git
cd speech-prep
uv sync  # or pip install -e .
```

## Quick Start

```python
from speech_prep import SoundFile
from pathlib import Path

# Load an audio file
audio = SoundFile(Path("recording.wav"))

if audio:
    print(f"Duration: {audio.duration:.2f} seconds")
    print(f"Format: {audio.format}")
    print(f"Silence periods detected: {len(audio.silence_periods)}")

    # Clean up the audio for speech-to-text
    cleaned = audio.strip(output_path=Path("recording_stripped.wav"))
    faster = cleaned.speed(output_path=Path("recording_stripped_fast.wav"), speed_factor=1.2)
    final = faster.convert(output_path=Path("clean.mp3"))

    print(f"Processed file saved: {final.path}")
```

## Usage Examples

### Basic Operations

```python
from speech_prep import SoundFile
from pathlib import Path

# Load audio file
audio = SoundFile(Path("interview.wav"))

# View audio information
print(audio)  # Shows duration, format, file size, and silence periods

# Remove silence from beginning and end
cleaned = audio.strip(output_path=Path("interview_stripped.wav"))

# Remove only leading silence
cleaned = audio.strip(output_path=Path("interview_leading.wav"), trailing=False)

# Speed up audio by 50%
faster = audio.speed(output_path=Path("interview_fast.wav"), speed_factor=1.5)

# Convert format
mp3_file = audio.convert(output_path=Path("output.mp3"))
```

### Processing Pipeline

```python
from speech_prep import SoundFile
from pathlib import Path

def prepare_for_transcription(input_file: Path, output_file: Path):
    """Prepare audio file for speech-to-text processing."""
    # Load the original file
    audio = SoundFile(input_file)
    if not audio:
        return None
    # Processing pipeline
    stripped = audio.strip(output_path=input_file.with_stem(input_file.stem + "_stripped"))
    faster = stripped.speed(output_path=input_file.with_stem(input_file.stem + "_stripped_fast"), speed_factor=1.1)
    processed = faster.convert(output_path=output_file)
    if processed:
        print(f"Original duration: {audio.duration:.2f}s")
        print(f"Processed duration: {processed.duration:.2f}s")
        print(f"Time saved: {audio.duration - processed.duration:.2f}s")
    return processed

# Use the pipeline
result = prepare_for_transcription(
    Path("long_meeting.wav"),
    Path("ready_for_stt.mp3")
)
```

### Error Handling

```python
from speech_prep import SoundFile, SpeechPrepError, FFmpegError
from pathlib import Path

try:
    audio = SoundFile(Path("audio.wav"))
    if audio:
        result = audio.strip().speed(2.0)
        print(f"Success: {result.path}")
    else:
        print("Failed to load audio file")

except FFmpegError as e:
    print(f"FFmpeg error: {e}")
    if e.stderr:
        print(f"Details: {e.stderr}")

except SpeechPrepError as e:
    print(f"Processing error: {e}")
```

### Custom Parameters

```python
from speech_prep import SoundFile
from pathlib import Path

# Custom silence detection settings
audio = SoundFile(
    Path("audio.wav"),
    noise_threshold_db=-40,    # More sensitive silence detection
    min_silence_duration=0.3   # Shorter minimum silence periods
)

# Custom output paths
cleaned = audio.strip(output_path=Path("custom_output.wav"))

# Custom conversion settings
mp3 = audio.convert(
    output_path=Path("output.mp3"),
    audio_bitrate="192k"  # Custom bitrate
)
```

## API Reference

### SoundFile Class

#### Constructor
```python
SoundFile(file_path, noise_threshold_db=-30, min_silence_duration=0.5)
```

#### Methods
- **`strip(output_path, leading=True, trailing=True)`**: Remove silence
- **`speed(output_path, speed_factor)`**: Adjust playback speed
- **`convert(output_path, audio_bitrate=None)`**: Convert format

#### Properties
- **`path`**: Path to the audio file
- **`duration`**: Duration in seconds
- **`format`**: Audio format
- **`file_size`**: File size in bytes
- **`silence_periods`**: List of detected silence periods
- **`median_silence`**: Median silence duration

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built on top of the powerful [FFmpeg](https://ffmpeg.org/) multimedia framework
