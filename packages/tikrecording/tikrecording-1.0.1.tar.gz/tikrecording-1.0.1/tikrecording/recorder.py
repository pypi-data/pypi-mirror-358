# file: tikrecording/recorder.py

import os
import time
import logging
import threading
from contextlib import suppress
from requests import RequestException

from .api import TikTokAPI
from .converter import Converter
from .exceptions import RecordingException, LiveNotFound

logger = logging.getLogger(__name__)

class Recorder:
    """Main class to manage the recording of a TikTok live session."""
    def __init__(self, username: str, cookies: dict = None, duration: int = None):
        self.username = username
        self.duration = duration
        self.api = TikTokAPI(cookies=cookies)
        
        self._stop_event = threading.Event()
        self.output_filepath = None
        self.cancellation_requested = False
    
    def _get_output_path(self, output_dir: str) -> str:
        """Creates and returns the full output file path."""
        user_dir = os.path.join(output_dir, self.username)
        os.makedirs(user_dir, exist_ok=True)
        filename = f"TK_{self.username}_{time.strftime('%Y%m%d_%H%M%S')}.flv"
        return os.path.join(user_dir, filename)

    def record(self, output_dir: str = "./recordings") -> str:
        """
        Starts the recording process. This is a blocking call that will
        wait for the user to go live and finish when the stream ends.
        """
        logger.info(f"Starting recording process for user: '{self.username}'")
        room_id = self.api.get_room_id_from_user(self.username)

        wait_intervals = [120, 300, 600, 900]  # 2m, 5m, 10m, then 15m
        interval_index = 0
        
        while not self._stop_event.is_set():
            if self.api.is_room_alive(room_id):
                logger.info(f"'{self.username}' is live. Starting download.")
                self._start_recording_session(room_id, output_dir)
                return self.output_filepath  # Return the final path after recording
            else:
                wait_time = wait_intervals[min(interval_index, len(wait_intervals) - 1)]
                logger.info(f"'{self.username}' is not live. Waiting for {wait_time // 60} minutes...")
                interval_index += 1
                self._stop_event.wait(wait_time)
        
        raise LiveNotFound(f"Process was stopped before '{self.username}' went live.")

    def _start_recording_session(self, room_id: str, output_dir: str):
        """Starts the stream download session and handles post-processing."""
        try:
            live_url = self.api.get_live_url(room_id)
            self.output_filepath = self._get_output_path(output_dir)
            logger.info(f"Recording '{self.username}' -> '{os.path.basename(self.output_filepath)}'")
            self._fetch_stream(live_url, self.output_filepath)
        finally:
            self.api.http_client.close()
            if self.cancellation_requested:
                logger.warning("Recording was cancelled. Deleting temporary file (if any).")
                if self.output_filepath and os.path.exists(self.output_filepath):
                    with suppress(OSError): os.remove(self.output_filepath)
            else:
                self._process_recorded_file()

    def _fetch_stream(self, live_url: str, output_file: str):
        """Downloads the stream content and saves it to a file."""
        start_time = time.time()
        try:
            with self.api.http_client.session.get(live_url, stream=True, timeout=10) as response:
                response.raise_for_status()
                with open(output_file, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if self._stop_event.is_set():
                            logger.info("Stop signal received, ending recording.")
                            break
                        if self.duration and (time.time() - start_time) > self.duration:
                            logger.info(f"Recording duration of {self.duration}s reached. Stopping.")
                            break
                        f.write(chunk)
        except RequestException as e:
            raise RecordingException(f"Connection error while downloading stream: {e}")

    def _process_recorded_file(self):
        """Processes the recorded file: converts FLV to MP4."""
        if self.output_filepath and os.path.exists(self.output_filepath):
            if os.path.getsize(self.output_filepath) > 1024:  # Valid file
                mp4_file = self.output_filepath.replace('.flv', '.mp4')
                Converter.to_mp4(self.output_filepath, mp4_file)
                os.remove(self.output_filepath)  # Delete original flv file
                self.output_filepath = mp4_file  # Update path to the final file
            else:
                os.remove(self.output_filepath)
                logger.warning("Recorded file is too small or corrupt, it has been deleted.")
                self.output_filepath = None

    def stop(self, cancel: bool = False):
        """Stops the recording or waiting process."""
        self.cancellation_requested = cancel
        self._stop_event.set()