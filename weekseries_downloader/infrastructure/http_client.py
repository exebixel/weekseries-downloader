"""
HTTP client for making web requests
"""

import urllib.request
import urllib.error
from typing import Optional, Dict
import logging


class HTTPClient:
    """HTTP client for making web requests"""

    def __init__(self, timeout: int = 30, user_agent: Optional[str] = None):
        """
        Initialize HTTP client

        Args:
            timeout: Request timeout in seconds
            user_agent: Custom user agent string
        """
        self.timeout = timeout
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) " "AppleWebKit/537.36 (KHTML, like Gecko) " "Chrome/131.0.0.0 Safari/537.36"
        )
        self.logger = logging.getLogger(__name__)

    def fetch(self, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[str]:
        """
        Fetch URL content with error handling

        Args:
            url: URL to fetch
            headers: Optional HTTP headers

        Returns:
            Page content or None if failed
        """
        if not url:
            return None

        try:
            req = self.create_request(url, headers)

            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                content = response.read().decode("utf-8")
                self.logger.debug(f"Successfully fetched URL: {url}")
                return content

        except urllib.error.HTTPError as e:
            self.logger.error(f"HTTP error fetching {url}: {e.code} {e.reason}")
            return None
        except urllib.error.URLError as e:
            self.logger.error(f"URL error fetching {url}: {e.reason}")
            return None
        except UnicodeDecodeError as e:
            self.logger.error(f"Encoding error fetching {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching {url}: {e}")
            return None

    def create_request(self, url: str, headers: Optional[Dict[str, str]] = None) -> urllib.request.Request:
        """
        Create configured urllib Request object

        Args:
            url: URL for the request
            headers: Optional custom headers

        Returns:
            Configured Request object
        """
        req = urllib.request.Request(url)

        # Use provided headers or default headers
        effective_headers = headers or self.get_default_headers()

        # Add all headers to request
        for key, value in effective_headers.items():
            req.add_header(key, value)

        return req

    def get_default_headers(self) -> Dict[str, str]:
        """
        Get default HTTP headers

        Returns:
            Dict with default headers
        """
        return {"User-Agent": self.user_agent, "Accept": "*/*", "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"}

    def get_weekseries_headers(self, referer: Optional[str] = None) -> Dict[str, str]:
        """
        Get headers configured for weekseries.info requests

        Args:
            referer: Custom referer URL

        Returns:
            Dict with weekseries-specific headers
        """
        headers = self.get_default_headers()
        headers.update(
            {
                "Referer": referer or "https://www.weekseries.info/",
                "Origin": "https://www.weekseries.info",
            }
        )
        return headers
