"""
URL parsing and validation for WeekSeries
"""

import re
from enum import Enum
from typing import Optional
from ..models import EpisodeInfo


class URLType(Enum):
    """Supported URL types"""

    WEEKSERIES = "weekseries"
    DIRECT_STREAM = "direct_stream"
    BASE64 = "base64"
    UNKNOWN = "unknown"


class URLParser:
    """Parse and validate WeekSeries URLs"""

    # Pre-compiled regex pattern for weekseries.info URLs
    WEEKSERIES_PATTERN = re.compile(r"https?://(?:www\.)?weekseries\.info/series/([^/]+)/temporada-(\d+)/episodio-(\d+)")

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Check if string is a valid HTTP(S) URL

        Args:
            url: String to check

        Returns:
            True if valid HTTP(S) URL
        """
        if not url:
            return False

        return url.startswith(("http://", "https://"))

    @staticmethod
    def is_weekseries_url(url: str) -> bool:
        """
        Check if URL is from weekseries.info

        Args:
            url: URL to check

        Returns:
            True if valid weekseries.info URL
        """
        if not url:
            return False

        if not url.startswith(("http://", "https://")):
            return False

        if "weekseries.info" not in url:
            return False

        return URLParser.WEEKSERIES_PATTERN.match(url) is not None

    @staticmethod
    def is_direct_stream_url(url: str) -> bool:
        """
        Check if URL is a direct m3u8/mpd stream

        Args:
            url: URL to check

        Returns:
            True if direct stream URL
        """
        if not url:
            return False

        if not url.startswith(("http://", "https://")):
            return False

        return url.endswith(".m3u8") or "stream" in url.lower()

    @staticmethod
    def is_base64_encoded(text: str) -> bool:
        """
        Check if string is base64-encoded URL

        Args:
            text: String to check

        Returns:
            True if valid base64 string
        """
        if not text:
            return False

        if len(text) < 4:
            return False

        # Check if matches base64 pattern
        if not re.match(r"^[A-Za-z0-9+/]*={0,2}$", text):
            return False

        return True

    @staticmethod
    def detect_url_type(url: str) -> URLType:
        """
        Detect the type of URL provided

        Args:
            url: URL to analyze

        Returns:
            URLType corresponding to detected type
        """
        if not url:
            return URLType.UNKNOWN

        if URLParser.is_weekseries_url(url):
            return URLType.WEEKSERIES

        if URLParser.is_direct_stream_url(url):
            return URLType.DIRECT_STREAM

        if URLParser.is_base64_encoded(url):
            return URLType.BASE64

        return URLType.UNKNOWN

    @staticmethod
    def extract_episode_info(url: str) -> Optional[EpisodeInfo]:
        """
        Extract episode info from weekseries URL

        Args:
            url: WeekSeries URL

        Returns:
            EpisodeInfo or None if invalid URL
        """
        if not URLParser.is_weekseries_url(url):
            return None

        match = URLParser.WEEKSERIES_PATTERN.match(url)
        if not match:
            return None

        series_name, season, episode = match.groups()

        return EpisodeInfo(series_name=series_name, season=int(season), episode=int(episode), original_url=url)
