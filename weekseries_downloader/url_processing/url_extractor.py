"""
URL extraction from WeekSeries pages using dependency injection
"""

from typing import Optional
import logging
from ..models import ExtractionResult
from ..infrastructure.http_client import HTTPClient
from ..infrastructure.parsers import HTMLParser, Base64Parser
from ..infrastructure.cache_manager import CacheManager
from .url_parser import URLParser


class URLExtractor:
    """Extract streaming URLs from WeekSeries pages"""

    def __init__(
        self, http_client: Optional[HTTPClient] = None, html_parser: Optional[HTMLParser] = None, cache_manager: Optional[CacheManager] = None
    ):
        """
        Initialize with dependency injection

        Args:
            http_client: HTTP client for requests
            html_parser: HTML parser for content extraction
            cache_manager: Cache manager for caching results
        """
        self.http_client = http_client or HTTPClient()
        self.html_parser = html_parser or HTMLParser()
        self.cache = cache_manager or CacheManager()
        self.logger = logging.getLogger(__name__)

    def extract_stream_url(self, page_url: str, use_cache: bool = True) -> ExtractionResult:
        """
        Extract streaming URL from weekseries page

        Args:
            page_url: WeekSeries page URL
            use_cache: Whether to use cache for extracted URLs

        Returns:
            ExtractionResult with:
            - success: bool
            - stream_url: Optional[str]
            - referer_url: Optional[str]
            - episode_info: Optional[EpisodeInfo]
            - error_message: Optional[str]
        """
        # Validate URL
        if not URLParser.is_weekseries_url(page_url):
            return ExtractionResult(success=False, error_message="URL is not from weekseries.info")

        # Check cache first
        if use_cache:
            cached_result = self.cache.get(page_url)
            if cached_result:
                self.logger.info(f"Using cached result for {page_url}")
                return cached_result

        # Fetch page content
        headers = self.http_client.get_weekseries_headers()
        content = self.http_client.fetch(page_url, headers)

        if not content:
            return ExtractionResult(success=False, error_message="Failed to fetch page content")

        # Parse HTML/JS for encoded URL
        encoded_url = self.html_parser.parse_stream_url(content)

        if not encoded_url:
            return ExtractionResult(success=False, error_message="Streaming URL not found on page")

        # Decode base64 URL
        stream_url = Base64Parser.decode(encoded_url)

        if not stream_url:
            return ExtractionResult(success=False, error_message="Failed to decode base64 URL")

        # Extract episode info
        episode_info = URLParser.extract_episode_info(page_url)

        # Build result
        result = ExtractionResult(success=True, stream_url=stream_url, referer_url=page_url, episode_info=episode_info)

        # Cache result
        if use_cache:
            self.cache.set(page_url, result)

        self.logger.info(f"Successfully extracted stream URL from {page_url}")
        return result

    @classmethod
    def create_default(cls) -> "URLExtractor":
        """
        Factory method with default dependencies

        Returns:
            URLExtractor with default configuration
        """
        return cls(http_client=HTTPClient(), html_parser=HTMLParser(), cache_manager=CacheManager())
