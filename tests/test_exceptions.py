"""
Tests for weekseries_downloader.exceptions module
"""

import pytest
from weekseries_downloader.exceptions import (
    ExtractionError,
    InvalidURLError,
    PageNotFoundError,
    ParsingError,
    NetworkError,
    DecodingError
)


class TestExtractionError:
    """Tests for ExtractionError base exception"""
    
    def test_extraction_error_creation_message_only(self):
        """Test ExtractionError creation with message only"""
        error = ExtractionError("Test error message")
        
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.url is None
    
    def test_extraction_error_creation_with_url(self):
        """Test ExtractionError creation with message and URL"""
        url = "https://example.com/test"
        error = ExtractionError("Test error message", url)
        
        expected_str = f"Test error message (URL: {url})"
        assert str(error) == expected_str
        assert error.message == "Test error message"
        assert error.url == url
    
    def test_extraction_error_inheritance(self):
        """Test ExtractionError inherits from Exception"""
        error = ExtractionError("Test message")
        
        assert isinstance(error, Exception)
        assert isinstance(error, ExtractionError)
    
    def test_extraction_error_can_be_raised(self):
        """Test ExtractionError can be raised and caught"""
        with pytest.raises(ExtractionError) as exc_info:
            raise ExtractionError("Test error")
        
        assert str(exc_info.value) == "Test error"
    
    def test_extraction_error_empty_message(self):
        """Test ExtractionError with empty message"""
        error = ExtractionError("")
        
        assert str(error) == ""
        assert error.message == ""


class TestInvalidURLError:
    """Tests for InvalidURLError exception"""
    
    def test_invalid_url_error_creation_basic(self):
        """Test InvalidURLError creation with URL only"""
        url = "invalid-url"
        error = InvalidURLError(url)

        expected_message = f"Invalid URL: {url}"
        assert error.message == expected_message
        assert error.url == url
        assert str(error) == f"{expected_message} (URL: {url})"
    
    def test_invalid_url_error_creation_with_expected_format(self):
        """Test InvalidURLError creation with expected format"""
        url = "invalid-url"
        expected_format = "https://example.com/format"
        error = InvalidURLError(url, expected_format)

        expected_message = f"Invalid URL: {url}. Expected format: {expected_format}"
        assert error.message == expected_message
        assert error.url == url
    
    def test_invalid_url_error_inheritance(self):
        """Test InvalidURLError inherits from ExtractionError"""
        error = InvalidURLError("test-url")
        
        assert isinstance(error, ExtractionError)
        assert isinstance(error, InvalidURLError)
    
    def test_invalid_url_error_can_be_raised(self):
        """Test InvalidURLError can be raised and caught"""
        url = "bad-url"

        with pytest.raises(InvalidURLError) as exc_info:
            raise InvalidURLError(url)

        assert exc_info.value.url == url
        assert "Invalid URL" in str(exc_info.value)


class TestPageNotFoundError:
    """Tests for PageNotFoundError exception"""
    
    def test_page_not_found_error_creation(self):
        """Test PageNotFoundError creation"""
        url = "https://example.com/not-found"
        error = PageNotFoundError(url)

        expected_message = "Page not found or episode does not exist"
        assert error.message == expected_message
        assert error.url == url
        assert str(error) == f"{expected_message} (URL: {url})"
    
    def test_page_not_found_error_inheritance(self):
        """Test PageNotFoundError inherits from ExtractionError"""
        error = PageNotFoundError("test-url")
        
        assert isinstance(error, ExtractionError)
        assert isinstance(error, PageNotFoundError)
    
    def test_page_not_found_error_can_be_raised(self):
        """Test PageNotFoundError can be raised and caught"""
        url = "https://example.com/missing"

        with pytest.raises(PageNotFoundError) as exc_info:
            raise PageNotFoundError(url)

        assert exc_info.value.url == url
        assert "not found" in str(exc_info.value)


class TestParsingError:
    """Tests for ParsingError exception"""
    
    def test_parsing_error_creation_basic(self):
        """Test ParsingError creation without details"""
        url = "https://example.com/page"
        error = ParsingError(url)

        expected_message = "Failed to find streaming URL on page"
        assert error.message == expected_message
        assert error.url == url
    
    def test_parsing_error_creation_with_details(self):
        """Test ParsingError creation with details"""
        url = "https://example.com/page"
        details = "No script tags found"
        error = ParsingError(url, details)

        expected_message = f"Failed to find streaming URL on page: {details}"
        assert error.message == expected_message
        assert error.url == url
    
    def test_parsing_error_inheritance(self):
        """Test ParsingError inherits from ExtractionError"""
        error = ParsingError("test-url")
        
        assert isinstance(error, ExtractionError)
        assert isinstance(error, ParsingError)
    
    def test_parsing_error_can_be_raised(self):
        """Test ParsingError can be raised and caught"""
        url = "https://example.com/page"
        details = "Pattern not found"
        
        with pytest.raises(ParsingError) as exc_info:
            raise ParsingError(url, details)
        
        assert exc_info.value.url == url
        assert details in str(exc_info.value)


class TestNetworkError:
    """Tests for NetworkError exception"""
    
    def test_network_error_creation_basic(self):
        """Test NetworkError creation without original error"""
        url = "https://example.com/endpoint"
        error = NetworkError(url)

        expected_message = "Network error accessing page"
        assert error.message == expected_message
        assert error.url == url
        assert error.original_error is None
    
    def test_network_error_creation_with_original_error(self):
        """Test NetworkError creation with original error"""
        url = "https://example.com/endpoint"
        original_error = ConnectionError("Connection refused")
        error = NetworkError(url, original_error)

        expected_message = f"Network error accessing page: {str(original_error)}"
        assert error.message == expected_message
        assert error.url == url
        assert error.original_error == original_error
    
    def test_network_error_inheritance(self):
        """Test NetworkError inherits from ExtractionError"""
        error = NetworkError("test-url")
        
        assert isinstance(error, ExtractionError)
        assert isinstance(error, NetworkError)
    
    def test_network_error_can_be_raised(self):
        """Test NetworkError can be raised and caught"""
        url = "https://example.com/endpoint"
        original_error = TimeoutError("Request timeout")
        
        with pytest.raises(NetworkError) as exc_info:
            raise NetworkError(url, original_error)
        
        assert exc_info.value.url == url
        assert exc_info.value.original_error == original_error
        assert "timeout" in str(exc_info.value).lower()


class TestDecodingError:
    """Tests for DecodingError exception"""
    
    def test_decoding_error_creation_basic(self):
        """Test DecodingError creation without original error"""
        encoded_url = "invalid-base64-string"
        error = DecodingError(encoded_url)

        expected_message = "Failed to decode base64 URL"
        assert error.message == expected_message
        assert error.encoded_url == encoded_url
        assert error.original_error is None
        # DecodingError doesn't inherit url from ExtractionError
        assert not hasattr(error, 'url') or error.url is None
    
    def test_decoding_error_creation_with_original_error(self):
        """Test DecodingError creation with original error"""
        encoded_url = "invalid-base64-string"
        original_error = ValueError("Invalid base64 character")
        error = DecodingError(encoded_url, original_error)

        expected_message = f"Failed to decode base64 URL: {str(original_error)}"
        assert error.message == expected_message
        assert error.encoded_url == encoded_url
        assert error.original_error == original_error
    
    def test_decoding_error_inheritance(self):
        """Test DecodingError inherits from ExtractionError"""
        error = DecodingError("test-encoded")
        
        assert isinstance(error, ExtractionError)
        assert isinstance(error, DecodingError)
    
    def test_decoding_error_can_be_raised(self):
        """Test DecodingError can be raised and caught"""
        encoded_url = "bad-base64"
        original_error = ValueError("Invalid padding")
        
        with pytest.raises(DecodingError) as exc_info:
            raise DecodingError(encoded_url, original_error)
        
        assert exc_info.value.encoded_url == encoded_url
        assert exc_info.value.original_error == original_error
        assert "padding" in str(exc_info.value).lower()


class TestExceptionChaining:
    """Tests for exception chaining and context"""
    
    def test_exception_chaining_with_original_error(self):
        """Test exception chaining preserves original error context"""
        original_error = ValueError("Original error message")
        
        try:
            raise original_error
        except ValueError as e:
            network_error = NetworkError("https://example.com", e)
            
            assert network_error.original_error == original_error
            assert "Original error message" in str(network_error)
    
    def test_multiple_exception_types_can_be_caught(self):
        """Test that different exception types can be caught appropriately"""
        exceptions_to_test = [
            InvalidURLError("bad-url"),
            PageNotFoundError("https://example.com/404"),
            ParsingError("https://example.com/page", "No patterns found"),
            NetworkError("https://example.com/endpoint"),
            DecodingError("bad-base64")
        ]
        
        for exception in exceptions_to_test:
            with pytest.raises(ExtractionError):
                raise exception
            
            # Also test specific exception type
            with pytest.raises(type(exception)):
                raise exception
    
    def test_exception_attributes_preserved(self):
        """Test that exception attributes are preserved when raised"""
        url = "https://example.com/test"
        original_error = TimeoutError("Request timed out")
        
        error = NetworkError(url, original_error)
        
        try:
            raise error
        except NetworkError as caught_error:
            assert caught_error.url == url
            assert caught_error.original_error == original_error
            assert caught_error.message == error.message