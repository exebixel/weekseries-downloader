"""
Parsers for HTML content and base64 encoding
"""

import re
import base64
from typing import Optional
import logging


class HTMLParser:
    """Parse HTML/JavaScript content for stream URLs"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Pre-compile regex patterns for performance
        self._patterns = [
            # Common pattern: JavaScript variable with base64
            re.compile(r'(?:src|url|stream|video)\s*[:=]\s*["\']([A-Za-z0-9+/]{20,}={0,2})["\']', re.IGNORECASE),
            # Pattern in data-* attributes
            re.compile(r'data-[^=]*=\s*["\']([A-Za-z0-9+/]{20,}={0,2})["\']', re.IGNORECASE),
            # Pattern in JavaScript strings
            re.compile(r'["\']([A-Za-z0-9+/]{40,}={0,2})["\']', re.IGNORECASE),
            # More generic pattern for long base64
            re.compile(r"([A-Za-z0-9+/]{50,}={0,2})", re.IGNORECASE),
        ]

    def parse_stream_url(self, content: str) -> Optional[str]:
        """
        Parse page content to extract base64-encoded stream URL

        Tries multiple patterns:
        1. JavaScript variable assignments
        2. Embedded JSON objects
        3. iframe src attributes
        4. Generic long base64 strings

        Args:
            content: Page HTML/JavaScript content

        Returns:
            Base64-encoded stream URL or None if not found
        """
        if not content:
            return None

        for pattern in self._patterns:
            matches = pattern.findall(content)

            for match in matches:
                # Verify if it looks like a stream URL
                if self._is_likely_stream_url(match):
                    self.logger.debug(f"Found potential stream URL (length: {len(match)})")
                    return match

        self.logger.warning("No stream URL found in content")
        return None

    def _is_likely_stream_url(self, base64_string: str) -> bool:
        """
        Check if base64 string probably contains a streaming URL

        Args:
            base64_string: Base64 string to verify

        Returns:
            True if probably a streaming URL
        """
        if not base64_string:
            return False

        if len(base64_string) < 20:
            return False

        # Try to decode to verify it contains URL
        try:
            decoded = Base64Parser.decode(base64_string)
            if not decoded:
                return False

            # Check for stream URL indicators
            stream_indicators = [".m3u8", "stream", "video", "http"]
            has_indicator = any(indicator in decoded.lower() for indicator in stream_indicators)

            # Check if it looks like a valid URL
            looks_like_url = decoded.startswith(("http://", "https://"))

            return has_indicator and looks_like_url

        except Exception:
            return False


class Base64Parser:
    """Parse and decode base64-encoded data"""

    @staticmethod
    def decode(encoded: str) -> Optional[str]:
        """
        Decode base64 string with error handling

        Args:
            encoded: Base64-encoded string

        Returns:
            Decoded string or None if failed
        """
        if not encoded:
            return None

        try:
            decoded = base64.b64decode(encoded).decode("utf-8")
            return decoded
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error decoding base64: {e}")
            return None
