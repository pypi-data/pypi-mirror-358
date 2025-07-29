# file: tikrecording/converter.py

import os
import shutil
import subprocess
import logging

from .exceptions import ConverterException

logger = logging.getLogger(__name__)

class Converter:
    """A class containing static methods for media file conversion using ffmpeg."""
    FFMPEG_PATH = shutil.which("ffmpeg")

    @classmethod
    def _run_ffmpeg(cls, args: list):
        """Internal method to run an ffmpeg command."""
        if not cls.FFMPEG_PATH:
            raise FileNotFoundError("ffmpeg was not found in the system's PATH. Please install ffmpeg.")
        
        command = [cls.FFMPEG_PATH] + args
        try:
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                text=True, encoding='utf-8', errors='ignore'
            )
            _, stderr = process.communicate()
            if process.returncode != 0:
                raise ConverterException(f"FFmpeg Error: {stderr.strip()}")
        except Exception as e:
            raise ConverterException(f"Failed to run FFmpeg: {e}")

    @classmethod
    def to_mp4(cls, input_flv: str, output_mp4: str):
        """Converts an FLV file to MP4 without re-encoding."""
        logger.info(f"Converting '{os.path.basename(input_flv)}' to MP4...")
        args = ["-i", input_flv, "-c", "copy", "-y", output_mp4]
        cls._run_ffmpeg(args)
        logger.info(f"Successfully converted to MP4: '{os.path.basename(output_mp4)}'")

    @classmethod
    def to_mp3(cls, input_video: str, output_mp3: str, bitrate: str = "128k"):
        """Extracts and converts audio from a video file to MP3."""
        logger.info(f"Converting '{os.path.basename(input_video)}' to MP3...")
        args = ["-i", input_video, "-vn", "-acodec", "mp3", "-ab", bitrate, "-y", output_mp3]
        cls._run_ffmpeg(args)
        logger.info(f"Successfully converted to MP3: '{os.path.basename(output_mp3)}'")

    @classmethod
    def to_wav(cls, input_file: str, output_wav: str):
        """Converts an audio/video file to WAV format."""
        logger.info(f"Converting '{os.path.basename(input_file)}' to WAV...")
        args = ["-i", input_file, "-acodec", "pcm_s16le", "-ar", "44100", "-y", output_wav]
        cls._run_ffmpeg(args)
        logger.info(f"Successfully converted to WAV: '{os.path.basename(output_wav)}'")