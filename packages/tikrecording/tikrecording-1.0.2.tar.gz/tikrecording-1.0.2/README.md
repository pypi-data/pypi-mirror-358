# TikRecording

[![PyPI version](https://badge.fury.io/py/tikrecording.svg)](https://badge.fury.io/py/tikrecording)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple and robust Python library for recording live sessions from TikTok. It handles finding users, waiting for their streams to start, and downloading the live video automatically.

## Key Features

- **Smart Waiting Mechanism**: Automatically polls for a user's live status with increasing intervals (2, 5, 10, then 15 minutes) to be efficient and avoid rate-limiting.
- **Automatic Conversion**: Downloads the raw `.flv` stream and automatically converts it to a standard `.mp4` container upon completion.
- **Standalone Converter**: Includes tools to convert video and audio files (e.g., to MP3, WAV) independently.
- **Graceful Stop**: The recording process can be stopped cleanly via a `stop()` method, allowing for safe interruption.
- **Cookie Support**: Allows using authentication cookies to access region-restricted or other specific live sessions.

## Prerequisites

- Python 3.8+
- **FFmpeg**: You must have FFmpeg installed on your system and available in your system's `PATH`. This is a hard requirement for all video processing and conversion tasks.

## Installation

Install the library from PyPI using pip:

```bash
pip install tikrecording
```

## Usage

Here are some basic examples of how to use the `tikrecording` library.

### Example 1: Record a User's Livestream

This example shows how to start recording a user. The script will wait if the user is not currently live.

```python
import logging
import threading
from tikrecording import Recorder, exceptions

# It's recommended to enable logging to see the library's progress
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')

# --- Configuration ---
TARGET_USERNAME = "some_tiktok_user"
OUTPUT_DIRECTORY = "./recordings"
# Provide cookies if the livestream is region-locked or requires authentication
COOKIES = {
    # "sessionid": "YOUR_SESSION_ID_HERE"
}
# ---------------------

recorder = Recorder(username=TARGET_USERNAME, cookies=COOKIES)

# It's best practice to run the blocking .record() method in a separate thread
# to allow for graceful shutdown via KeyboardInterrupt (Ctrl+C).
record_thread = threading.Thread(target=recorder.record, args=(OUTPUT_DIRECTORY,))

try:
    record_thread.start()
    # The main thread waits here until the recording thread is finished
    # This loop allows the program to catch KeyboardInterrupt on Windows
    while record_thread.is_alive():
        record_thread.join(timeout=1.0)

except KeyboardInterrupt:
    logging.warning("\nCtrl+C detected. Stopping the recorder gracefully...")
    # The .stop() method signals the recording thread to finish up and exit
    recorder.stop()
    # Wait for the thread to clean up and close
    record_thread.join()

except exceptions.UserLiveException as e:
    logging.error(f"A user or live session error occurred: {e}")
except exceptions.RecordingException as e:
    logging.error(f"An error occurred during recording: {e}")
except FileNotFoundError:
    logging.error("FFmpeg not found. Please install it and ensure it's in your system's PATH.")
except Exception as e:
    logging.critical(f"An unexpected error occurred: {e}", exc_info=True)

```

### Example 2: Using the Standalone Converter

If you already have a video file, you can use the `Converter` to change its format.

```python
from tikrecording import Converter, exceptions

try:
    # Convert a video to MP3
    print("Converting video to MP3...")
    Converter.to_mp3(
        input_video="path/to/your/video.mp4",
        output_mp3="path/to/your/audio.mp3",
        bitrate="192k"  # Optional bitrate
    )
    print("MP3 conversion successful!")

except exceptions.ConverterException as e:
    print(f"A conversion error occurred: {e}")
except FileNotFoundError:
    print("Error: ffmpeg is not installed or not in your system's PATH.")

```

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
