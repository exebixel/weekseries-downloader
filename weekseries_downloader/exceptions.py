"""
Custom exceptions for weekseries downloader
"""


class ExtractionError(Exception):
    """Base error for URL extraction"""

    def __init__(self, message: str, url: str = None):
        super().__init__(message)
        self.message = message
        self.url = url

    def __str__(self) -> str:
        if self.url:
            return f"{self.message} (URL: {self.url})"
        return self.message


class InvalidURLError(ExtractionError):
    """URL does not follow expected pattern"""

    def __init__(self, url: str, expected_format: str = None):
        message = f"Invalid URL: {url}"
        if expected_format:
            message += f". Expected format: {expected_format}"
        super().__init__(message, url)


class PageNotFoundError(ExtractionError):
    """Page/episode not found"""

    def __init__(self, url: str):
        message = "Page not found or episode does not exist"
        super().__init__(message, url)


class ParsingError(ExtractionError):
    """Failed to parse page content"""

    def __init__(self, url: str, details: str = None):
        message = "Failed to find streaming URL on page"
        if details:
            message += f": {details}"
        super().__init__(message, url)


class NetworkError(ExtractionError):
    """Network error during request"""

    def __init__(self, url: str, original_error: Exception = None):
        message = "Network error accessing page"
        if original_error:
            message += f": {str(original_error)}"
        super().__init__(message, url)
        self.original_error = original_error


class DecodingError(ExtractionError):
    """Failed to decode base64 URL"""

    def __init__(self, encoded_url: str, original_error: Exception = None):
        message = "Failed to decode base64 URL"
        if original_error:
            message += f": {str(original_error)}"
        super().__init__(message)
        self.encoded_url = encoded_url
        self.original_error = original_error


# Helper functions for creating exceptions with context


def create_invalid_url_error(url: str) -> InvalidURLError:
    """Create invalid URL error with expected format"""
    expected = "https://www.weekseries.info/series/[series]/temporada-[number]/episodio-[number]"
    return InvalidURLError(url, expected)


def create_parsing_error(url: str, content_length: int = None) -> ParsingError:
    """Create parsing error with content details"""
    details = None
    if content_length is not None:
        if content_length == 0:
            details = "empty page"
        elif content_length < 1000:
            details = "content too small"
        else:
            details = f"{content_length} characters processed"

    return ParsingError(url, details)


def create_network_error(url: str, original_error: Exception) -> NetworkError:
    """Create network error with original exception context"""
    return NetworkError(url, original_error)
