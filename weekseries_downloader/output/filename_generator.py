"""
Automatic filename generation from URLs and episode information
"""

import re
from typing import Optional
from urllib.parse import urlparse
import logging
from ..models import EpisodeInfo


class FilenameGenerator:
    """Generate intelligent output filenames"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._streaming_indicators = [".m3u8", "stream", "playlist", "video", "media"]

    def generate(
        self, stream_url: str, episode_info: Optional[EpisodeInfo] = None, user_output: Optional[str] = None, default_extension: str = ".mp4"
    ) -> str:
        """
        Generate output filename with multiple strategies

        Priority:
        1. User-provided output (if given)
        2. Episode info (series_S##E##.mp4)
        3. Extract from stream URL patterns
        4. Fallback to "video.mp4"

        Args:
            stream_url: Stream URL to extract name from
            episode_info: Episode information if available
            user_output: User-provided filename
            default_extension: Default file extension

        Returns:
            Sanitized filename
        """
        # Strategy 1: User provided
        if user_output and user_output != "video.mp4":
            self.logger.debug(f"Using custom filename: {user_output}")
            return self._ensure_extension(user_output, default_extension)

        # Strategy 2: Episode info
        if episode_info:
            filename = f"{episode_info.filename_safe_name}{default_extension}"
            self.logger.info(f"Automatic filename from episode info: {filename}")
            return filename

        # Strategy 3: Extract from URL
        extracted = self._extract_from_url(stream_url)
        if extracted:
            filename = extracted + default_extension
            self.logger.info(f"Filename from URL: {filename}")
            return filename

        # Strategy 4: Fallback
        fallback = f"video{default_extension}"
        self.logger.debug(f"Using fallback filename: {fallback}")
        return fallback

    def _extract_from_url(self, url: str) -> Optional[str]:
        """
        Try multiple URL patterns to extract filename

        Args:
            url: URL to extract from

        Returns:
            Extracted filename (without extension) or None
        """
        if not url:
            return None

        self.logger.debug(f"Extracting filename from URL: {url}")

        # Check if it's a streaming URL
        if not self._is_streaming_url(url):
            return None

        # Try different extraction strategies
        strategies = [
            self._extract_from_temporada_pattern,
            self._extract_from_season_pattern,
            self._extract_from_path_segments,
            self._extract_from_domain_and_path,
        ]

        for strategy in strategies:
            result = strategy(url)
            if result:
                self.logger.debug(f"Extracted using {strategy.__name__}: {result}")
                return result

        self.logger.debug("No recognized pattern in URL")
        return None

    def _is_streaming_url(self, url: str) -> bool:
        """Check if URL is a streaming URL"""
        return any(indicator in url.lower() for indicator in self._streaming_indicators)

    def _extract_from_temporada_pattern(self, url: str) -> Optional[str]:
        """
        Extract name using serie/temporada/episodio pattern

        Examples:
        - /the-good-doctor/02-temporada/16/stream.m3u8
        - /breaking-bad/05-temporada/14/playlist.m3u8
        """
        parts = url.split("/")

        for i, part in enumerate(parts):
            if "temporada" in part.lower() and i > 0 and i < len(parts) - 1:
                serie = self._clean_name(parts[i - 1])
                temporada = self._clean_name(part)
                episodio = self._clean_name(parts[i + 1]) if i + 1 < len(parts) else "01"
                return f"{serie}_{temporada}_{episodio}"

        return None

    def _extract_from_season_pattern(self, url: str) -> Optional[str]:
        """
        Extract name using serie/season-XX/episode-XX pattern

        Examples:
        - /the-office/season-09/episode-23/stream.m3u8
        - /friends/season-10/episode-01/playlist.m3u8
        """
        parts = url.split("/")

        for i, part in enumerate(parts):
            if "season" in part.lower() and i > 0 and i < len(parts) - 1:
                serie = self._clean_name(parts[i - 1])
                season = self._clean_name(part)
                episode = self._clean_name(parts[i + 1]) if i + 1 < len(parts) else "01"
                return f"{serie}_{season}_{episode}"

        return None

    def _extract_from_path_segments(self, url: str) -> Optional[str]:
        """
        Extract name from last path segments

        Examples:
        - /content/stranger-things/04-temporada/09/index.m3u8
        - /videos/game-of-thrones/08-temporada/06/stream.m3u8
        """
        parts = url.split("/")

        # Filter relevant parts (remove final file and empty parts)
        relevant_parts = [p for p in parts[-4:-1] if p and not p.endswith((".m3u8", ".ts", ".mp4")) and p != "stream"]

        if len(relevant_parts) >= 2:
            # Assume first is series, others are season/episode
            serie = self._clean_name(relevant_parts[0])
            extras = "_".join(self._clean_name(p) for p in relevant_parts[1:])
            return f"{serie}_{extras}"

        return None

    def _extract_from_domain_and_path(self, url: str) -> Optional[str]:
        """
        Extract name using domain and path as fallback

        Examples:
        - https://example.com/simple/stream.m3u8 -> example_simple
        """
        try:
            parsed = urlparse(url)
            domain_parts = parsed.netloc.split(".")
            path_parts = [p for p in parsed.path.split("/") if p and not p.endswith((".m3u8", ".ts"))]

            # Use main domain part + last path segments
            if domain_parts and path_parts:
                domain_name = self._clean_name(domain_parts[0])
                path_name = "_".join(self._clean_name(p) for p in path_parts[-2:])
                return f"{domain_name}_{path_name}"

        except Exception as e:
            self.logger.debug(f"Error extracting from domain/path: {e}")

        return None

    @staticmethod
    def _clean_name(name: str) -> str:
        """
        Clean name for filesystem use

        Args:
            name: Name to clean

        Returns:
            Clean and safe filename
        """
        if not name:
            return ""

        # Remove special characters and replace with underscore
        cleaned = re.sub(r'[<>:"/\\|?*]', "_", name)

        # Replace spaces and hyphens with underscores for consistency
        cleaned = cleaned.replace(" ", "_").replace("-", "_")

        # Remove multiple consecutive underscores
        cleaned = re.sub(r"_+", "_", cleaned)

        # Remove underscores at start and end
        cleaned = cleaned.strip("_")

        return cleaned.lower()

    @staticmethod
    def _ensure_extension(filename: str, default_ext: str) -> str:
        """
        Ensure filename has video extension

        Args:
            filename: Filename to check
            default_ext: Default extension to add

        Returns:
            Filename with extension
        """
        if not filename.endswith((".mp4", ".ts")):
            return filename + default_ext

        return filename

    @staticmethod
    def validate_filename(filename: str) -> str:
        """
        Validate and correct filename

        Args:
            filename: Filename to validate

        Returns:
            Valid filename
        """
        if not filename:
            return "video.mp4"

        # Remove invalid characters
        valid_name = re.sub(r'[<>:"/\\|?*]', "_", filename)

        # Ensure not empty after cleaning
        if not valid_name.strip():
            return "video.mp4"

        # Ensure extension
        if not valid_name.endswith((".mp4", ".ts")):
            valid_name += ".mp4"

        return valid_name
