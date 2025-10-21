"""
M3U8 playlist parser for HLS streams
"""

from typing import List, Optional
from urllib.parse import urljoin
import logging


class PlaylistParser:
    """Parse HLS m3u8 playlists"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def is_master_playlist(self, content: str) -> bool:
        """
        Check if playlist is a master playlist (multiple qualities)

        Args:
            content: Playlist content

        Returns:
            True if master playlist
        """
        return "#EXT-X-STREAM-INF" in content

    def get_first_quality_url(self, content: str, base_url: str) -> Optional[str]:
        """
        Extract first quality variant from master playlist

        Args:
            content: Master playlist content
            base_url: Base URL for resolving relative URLs

        Returns:
            URL of first quality playlist or None if not found
        """
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if line.startswith("#EXT-X-STREAM-INF"):
                # Next line is the playlist URL
                if i + 1 < len(lines):
                    playlist_path = lines[i + 1].strip()
                    playlist_url = self.make_absolute_url(playlist_path, base_url)
                    self.logger.info(f"Selected quality playlist: {playlist_url}")
                    return playlist_url

        self.logger.warning("No quality playlist found in master playlist")
        return None

    def parse_segments(self, content: str, base_url: str) -> List[str]:
        """
        Parse segment URLs from m3u8 playlist

        Args:
            content: Playlist content
            base_url: Base URL for resolving relative URLs

        Returns:
            List of absolute segment URLs
        """
        segments = []
        lines = content.split("\n")

        for line in lines:
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            # Convert relative URL to absolute
            segment_url = self.make_absolute_url(line, base_url)
            segments.append(segment_url)

        self.logger.debug(f"Parsed {len(segments)} segments from playlist")
        return segments

    @staticmethod
    def make_absolute_url(segment: str, base_url: str) -> str:
        """
        Convert relative segment URL to absolute

        Args:
            segment: Segment URL (relative or absolute)
            base_url: Base URL

        Returns:
            Absolute URL
        """
        if segment.startswith("http"):
            return segment

        return urljoin(base_url, segment)

    def get_base_url(self, playlist_url: str) -> str:
        """
        Get base URL from playlist URL

        Args:
            playlist_url: Full playlist URL

        Returns:
            Base URL (directory containing playlist)
        """
        return playlist_url.rsplit("/", 1)[0] + "/"
