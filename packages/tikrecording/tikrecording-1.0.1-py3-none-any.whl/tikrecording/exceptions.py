# file: tikrecording/exceptions.py

class TikTokException(Exception):
    """Base exception for issues related to the TikTok API."""
    pass

class UserLiveException(TikTokException):
    """Exception for issues related to the user's live status (not found, not live, etc.)."""
    pass

class LiveNotFound(UserLiveException):
    """Exception when the livestream is found but the stream URL cannot be retrieved."""
    pass

class RecordingException(Exception):
    """Exception for errors that occur while downloading the stream."""
    pass

class ConverterException(Exception):
    """Exception for errors that occur during file format conversion."""
    pass