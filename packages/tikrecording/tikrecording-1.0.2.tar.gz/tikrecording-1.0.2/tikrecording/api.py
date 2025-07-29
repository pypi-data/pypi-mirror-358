# file: tikrecording/api.py

import json
import re
import logging
from requests import Session, RequestException
from tenacity import retry, stop_after_attempt, wait_exponential

from .exceptions import TikTokException, UserLiveException, LiveNotFound

logger = logging.getLogger(__name__)

class HttpClient:
    """Manages HTTP requests with a shared session and headers."""
    def __init__(self, cookies: dict = None):
        self.session = Session()
        self.session.trust_env = False
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.tiktok.com/",
        })
        if cookies:
            self.session.cookies.update(cookies)

    def close(self):
        self.session.close()

class TikTokAPI:
    """Contains methods to interact with TikTok's API."""
    BASE_URL = "https://www.tiktok.com"
    WEBCAST_URL = "https://webcast.tiktok.com/webcast"

    def __init__(self, cookies: dict = None):
        self.http_client = HttpClient(cookies)

    def get_room_id_from_user(self, username: str) -> str:
        """Fetches the room_id from a user's live page."""
        url = f"{self.BASE_URL}/@{username}/live"
        try:
            response = self.http_client.session.get(url, timeout=10)
            response.raise_for_status()

            match = re.search(r'<script id="SIGI_STATE" type="application/json">(.*?)</script>', response.text)
            if not match:
                raise TikTokException("Could not find SIGI_STATE on the page. The API may have changed.")

            data = json.loads(match.group(1))
            live_room_data = data.get('LiveRoom', {}).get('liveRoomUserInfo', {})
            room_id = live_room_data.get('user', {}).get('roomId')

            if not room_id:
                raise UserLiveException(f"Could not find RoomID for user '{username}'. The user may not exist or has no live room.")
            
            logger.info(f"Found RoomID for '{username}': {room_id}")
            return str(room_id)

        except RequestException as e:
            if e.response and e.response.status_code == 404:
                raise UserLiveException(f"User '{username}' not found.")
            raise TikTokException(f"Network error while fetching RoomID: {e}")
        except (json.JSONDecodeError, KeyError) as e:
            raise TikTokException(f"Error processing API data (JSON or Key error): {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    def is_room_alive(self, room_id: str) -> bool:
        """Checks if a live room is currently active."""
        url = f"{self.WEBCAST_URL}/room/info/?aid=1988&room_id={room_id}"
        try:
            response = self.http_client.session.get(url, timeout=5)
            if response.status_code != 200:
                return False
            data = response.json()
            # Status 2: Live, Status 4: Live ended
            return data.get('data', {}).get('status', 0) == 2
        except RequestException:
            logger.warning(f"Request to check live status for room {room_id} failed, retrying...")
            return False

    def get_live_url(self, room_id: str) -> str:
        """Gets the FLV stream URL from the live room info."""
        url = f"{self.WEBCAST_URL}/room/info/?aid=1988&room_id={room_id}"
        try:
            response = self.http_client.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json().get('data', {})

            if data.get('status', 0) != 2:
                raise LiveNotFound("User is not currently live.")

            stream_data = data.get('stream_url', {}).get('flv_pull_url', {})
            live_url = stream_data.get('FULL_HD1') or stream_data.get('HD1') or stream_data.get('SD1') or stream_data.get('SD2')
            
            if not live_url:
                raise LiveNotFound("Could not find FLV stream URL in API data.")
            return live_url
        except (RequestException, json.JSONDecodeError) as e:
            raise LiveNotFound(f"Could not retrieve livestream URL: {e}")