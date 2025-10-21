"""
URL decoding and transformation utilities
"""

import base64
from typing import Optional
import logging


class URLDecoder:
    """Decode and transform URLs"""

    @staticmethod
    def decode_base64(encoded: str) -> Optional[str]:
        """
        Decode base64-encoded URL

        Args:
            encoded: Base64-encoded string

        Returns:
            Decoded URL or None if failed
        """
        if not encoded:
            return None

        try:
            decoded = base64.b64decode(encoded).decode("utf-8")
            return decoded
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error decoding base64 URL: {e}")
            return None

    @staticmethod
    def clean_url(url: str) -> str:
        """
        Remove URL parameters and fragments

        Args:
            url: URL to clean

        Returns:
            Cleaned URL
        """
        if not url:
            return url

        # Remove fragments (#)
        if "#" in url:
            url = url.split("#")[0]

        # Remove query parameters (?)
        if "?" in url:
            url = url.split("?")[0]

        return url

    @staticmethod
    def extract_url_from_text(text: str) -> Optional[str]:
        """
        Extract first URL from text content

        Args:
            text: Text containing URL

        Returns:
            Extracted URL or None if not found
        """
        if not text:
            return None

        import re

        url_pattern = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')
        match = url_pattern.search(text)

        if match:
            return match.group(0)

        return None
