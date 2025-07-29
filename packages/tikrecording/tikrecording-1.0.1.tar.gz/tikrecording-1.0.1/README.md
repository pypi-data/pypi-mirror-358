# TikRecording

A simple and effective Python library to record live sessions from TikTok.

## Features

- Automatically finds and waits for a user to go live.
- Records the stream at the best available quality.
- Automatically converts the initial `.flv` file to `.mp4`.
- Provides tools to convert to `.mp3`, `.wav`, and other formats.
- Object-oriented and easy-to-use API.

## Installation

```bash
pip install .
pip install tikrecording
```

##Usage
Here is a basic example to record a user's livestream.

import logging
from tikrecording import Recorder, exceptions

# Enable logging to see the progress
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Provide cookies if needed (for restricted lives)
my_cookies = {
    "sessionid": "YOUR_SESSION_ID_VALUE"
}

try:
    # 1. Initialize the recorder for your target user
    recorder = Recorder(username="some_tiktok_user", cookies=my_cookies)

    # 2. Start recording. The script will wait if the user is not live.
    # The file will be saved in 'recordings/some_tiktok_user/'
    output_file = recorder.record(output_dir="./recordings")

    if output_file:
        print(f"Success! Video saved at: {output_file}")

except exceptions.UserLiveException as e:
    print(f"User Error: {e}")
except exceptions.RecordingException as e:
    print(f"Recording Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")