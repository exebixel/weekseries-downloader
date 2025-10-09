"""
Tests for weekseries_downloader.utils module
"""

import pytest
from unittest.mock import patch, Mock
import subprocess
import urllib.request
from weekseries_downloader.utils import (
    decode_base64_url,
    sanitize_filename,
    check_ffmpeg,
    create_request
)


class TestDecodeBase64Url:
    """Tests for decode_base64_url function"""
    
    def test_decode_valid_base64_url(self, valid_base64_urls):
        """Test decoding valid base64 URLs"""
        # Test first URL: https://example.com/stream.m3u8
        decoded = decode_base64_url(valid_base64_urls[0])
        assert decoded == "https://example.com/stream.m3u8"
        
        # Test second URL: http://test.com/video.m3u8
        decoded = decode_base64_url(valid_base64_urls[1])
        assert decoded == "http://test.com/video.m3u8"
    
    def test_decode_invalid_base64_strings(self, invalid_base64_strings):
        """Test decoding invalid base64 strings"""
        for invalid_string in invalid_base64_strings:
            result = decode_base64_url(invalid_string)
            # Empty string decodes to empty string, None returns None
            if invalid_string == "":
                assert result == ""
            elif invalid_string is None:
                assert result is None
            else:
                assert result is None
    
    def test_decode_base64_url_empty_string(self):
        """Test decode_base64_url with empty string"""
        result = decode_base64_url("")
        # Empty string decodes to empty string
        assert result == ""
    
    def test_decode_base64_url_none(self):
        """Test decode_base64_url with None input"""
        result = decode_base64_url(None)
        assert result is None
    
    def test_decode_base64_url_corrupted_padding(self):
        """Test decode_base64_url with corrupted padding"""
        # Valid base64 but with wrong padding
        corrupted = "aHR0cHM6Ly9leGFtcGxlLmNvbS9zdHJlYW0ubTN1OA"  # Missing ==
        result = decode_base64_url(corrupted)
        # Python's base64 decoder is strict about padding
        assert result is None
    
    def test_decode_base64_url_non_utf8(self):
        """Test decode_base64_url with non-UTF8 content"""
        import base64
        # Create base64 of invalid UTF-8 bytes
        invalid_utf8_bytes = b'\xff\xfe\xfd'
        encoded = base64.b64encode(invalid_utf8_bytes).decode('ascii')
        
        result = decode_base64_url(encoded)
        assert result is None
    
    def test_decode_base64_url_special_characters(self):
        """Test decode_base64_url with special characters in result"""
        import base64
        special_url = "https://example.com/path?param=value&other=123"
        encoded = base64.b64encode(special_url.encode('utf-8')).decode('ascii')
        
        result = decode_base64_url(encoded)
        assert result == special_url
    
    def test_decode_base64_url_unicode_content(self):
        """Test decode_base64_url with Unicode content"""
        import base64
        unicode_content = "https://example.com/série-título"
        encoded = base64.b64encode(unicode_content.encode('utf-8')).decode('ascii')
        
        result = decode_base64_url(encoded)
        assert result == unicode_content


class TestSanitizeFilename:
    """Tests for sanitize_filename function"""
    
    def test_sanitize_filename_basic(self):
        """Test sanitize_filename with basic filename"""
        result = sanitize_filename("normal_filename.mp4")
        assert result == "normal_filename.mp4"
    
    def test_sanitize_filename_special_characters(self):
        """Test sanitize_filename removes filesystem special characters"""
        filename = 'test<>:"/\\|?*file.mp4'
        expected = "test_________file.mp4"
        result = sanitize_filename(filename)
        assert result == expected
    
    def test_sanitize_filename_individual_characters(self):
        """Test sanitize_filename with each special character individually"""
        test_cases = [
            ("file<name.mp4", "file_name.mp4"),
            ("file>name.mp4", "file_name.mp4"),
            ("file:name.mp4", "file_name.mp4"),
            ('file"name.mp4', "file_name.mp4"),
            ("file/name.mp4", "file_name.mp4"),
            ("file\\name.mp4", "file_name.mp4"),
            ("file|name.mp4", "file_name.mp4"),
            ("file?name.mp4", "file_name.mp4"),
            ("file*name.mp4", "file_name.mp4"),
        ]
        
        for input_filename, expected in test_cases:
            result = sanitize_filename(input_filename)
            assert result == expected, f"Failed for input: {input_filename}"
    
    def test_sanitize_filename_unicode_characters(self):
        """Test sanitize_filename with Unicode characters"""
        filename = "série_título_episódio.mp4"
        result = sanitize_filename(filename)
        # Unicode characters should be preserved
        assert result == "série_título_episódio.mp4"
    
    def test_sanitize_filename_mixed_content(self):
        """Test sanitize_filename with mixed valid and invalid characters"""
        filename = "The Good Doctor - S01E03 - Oliver's Story.mp4"
        expected = "The Good Doctor - S01E03 - Oliver's Story.mp4"
        result = sanitize_filename(filename)
        assert result == expected
    
    def test_sanitize_filename_only_special_characters(self):
        """Test sanitize_filename with only special characters"""
        filename = '<>:"/\\|?*'
        expected = "_________"
        result = sanitize_filename(filename)
        assert result == expected
    
    def test_sanitize_filename_empty_string(self):
        """Test sanitize_filename with empty string"""
        result = sanitize_filename("")
        assert result == ""
    
    def test_sanitize_filename_very_long_name(self):
        """Test sanitize_filename with very long filename"""
        long_name = "a" * 200 + "<>:" + "b" * 100 + ".mp4"
        result = sanitize_filename(long_name)
        expected = "a" * 200 + "___" + "b" * 100 + ".mp4"
        assert result == expected
        assert len(result) == len(expected)
    
    def test_sanitize_filename_path_separators(self):
        """Test sanitize_filename specifically with path separators"""
        # These should be replaced to prevent directory traversal
        filename = "../../../etc/passwd"
        result = sanitize_filename(filename)
        expected = ".._.._.._etc_passwd"  # Only / and \ are replaced, not .
        assert result == expected
        assert "/" not in result
        assert "\\" not in result
    
    def test_sanitize_filename_windows_reserved_names(self):
        """Test sanitize_filename with Windows reserved device names"""
        # These are valid filenames on Unix but reserved on Windows
        reserved_names = ["CON.mp4", "PRN.mp4", "AUX.mp4", "NUL.mp4"]
        for name in reserved_names:
            result = sanitize_filename(name)
            # Should not change these on Unix systems
            assert result == name
    
    def test_sanitize_filename_preserves_extensions(self):
        """Test sanitize_filename preserves file extensions"""
        test_cases = [
            ("file<name>.mp4", "file_name_.mp4"),
            ("file:name.ts", "file_name.ts"),
            ("file|name.mkv", "file_name.mkv"),
            ("file?name", "file_name"),  # No extension
        ]
        
        for input_filename, expected in test_cases:
            result = sanitize_filename(input_filename)
            assert result == expected

class TestCheckFfmpeg:
    """Tests for check_ffmpeg function"""
    
    def test_check_ffmpeg_installed_success(self, mock_subprocess_success):
        """Test check_ffmpeg when ffmpeg is installed and working"""
        result = check_ffmpeg()
        assert result is True
        
        # Verify subprocess.run was called with correct arguments
        mock_subprocess_success.assert_called_once_with(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    
    def test_check_ffmpeg_not_installed(self, mock_subprocess_failure):
        """Test check_ffmpeg when ffmpeg is not installed"""
        result = check_ffmpeg()
        assert result is False
        
        # Verify subprocess.run was called
        mock_subprocess_failure.assert_called_once_with(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    
    @patch('weekseries_downloader.utils.subprocess.run')
    def test_check_ffmpeg_command_error(self, mock_run):
        """Test check_ffmpeg when ffmpeg command fails"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'ffmpeg')
        
        result = check_ffmpeg()
        assert result is False
    
    @patch('weekseries_downloader.utils.subprocess.run')
    def test_check_ffmpeg_permission_error(self, mock_run):
        """Test check_ffmpeg when there's a permission error"""
        mock_run.side_effect = PermissionError("Permission denied")
        
        # PermissionError is not caught by check_ffmpeg, so it should raise
        with pytest.raises(PermissionError):
            check_ffmpeg()
    
    @patch('weekseries_downloader.utils.subprocess.run')
    def test_check_ffmpeg_other_exception(self, mock_run):
        """Test check_ffmpeg with other unexpected exceptions"""
        mock_run.side_effect = OSError("Unexpected error")
        
        # OSError is not caught by check_ffmpeg, so it should raise
        with pytest.raises(OSError):
            check_ffmpeg()
    
    @patch('weekseries_downloader.utils.subprocess.run')
    def test_check_ffmpeg_successful_return_code(self, mock_run):
        """Test check_ffmpeg with successful return code"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        result = check_ffmpeg()
        assert result is True


class TestCreateRequest:
    """Tests for create_request function"""
    
    def test_create_request_basic_url(self):
        """Test create_request with basic URL"""
        url = "https://example.com/test"
        req = create_request(url)
        
        assert isinstance(req, urllib.request.Request)
        assert req.full_url == url
    
    def test_create_request_default_headers(self):
        """Test create_request sets default headers"""
        url = "https://example.com/test"
        req = create_request(url)
        
        # Check User-Agent header
        user_agent = req.get_header('User-agent')
        assert user_agent is not None
        assert 'Mozilla/5.0' in user_agent
        assert 'Chrome' in user_agent
        
        # Check default referer
        referer = req.get_header('Referer')
        assert referer == "https://www.weekseries.info/"
        
        # Check Origin header
        origin = req.get_header('Origin')
        assert origin == "https://www.weekseries.info"
        
        # Check Accept header
        accept = req.get_header('Accept')
        assert accept == "*/*"
        
        # Check Accept-Language header
        accept_lang = req.get_header('Accept-language')
        assert accept_lang == "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    
    def test_create_request_custom_referer(self):
        """Test create_request with custom referer"""
        url = "https://example.com/test"
        custom_referer = "https://custom-referer.com/"
        req = create_request(url, referer=custom_referer)
        
        referer = req.get_header('Referer')
        assert referer == custom_referer
    
    def test_create_request_none_referer(self):
        """Test create_request with None referer uses default"""
        url = "https://example.com/test"
        req = create_request(url, referer=None)
        
        referer = req.get_header('Referer')
        assert referer == "https://www.weekseries.info/"
    
    def test_create_request_empty_referer(self):
        """Test create_request with empty string referer"""
        url = "https://example.com/test"
        req = create_request(url, referer="")
        
        referer = req.get_header('Referer')
        # Empty string is falsy, so default referer is used
        assert referer == "https://www.weekseries.info/"
    
    def test_create_request_user_agent_format(self):
        """Test create_request User-Agent format is correct"""
        url = "https://example.com/test"
        req = create_request(url)
        
        user_agent = req.get_header('User-agent')
        expected_parts = [
            "Mozilla/5.0",
            "Macintosh; Intel Mac OS X 10_15_7",
            "AppleWebKit/537.36",
            "KHTML, like Gecko",
            "Chrome/131.0.0.0",
            "Safari/537.36"
        ]
        
        for part in expected_parts:
            assert part in user_agent
    
    def test_create_request_different_urls(self):
        """Test create_request with different URL formats"""
        test_urls = [
            "https://example.com",
            "http://test.com/path",
            "https://subdomain.example.com/path/to/resource?param=value",
            "https://example.com:8080/secure/path"
        ]
        
        for url in test_urls:
            req = create_request(url)
            assert req.full_url == url
            assert req.get_header('User-agent') is not None
    
    def test_create_request_headers_immutable(self):
        """Test that headers are set correctly and don't interfere"""
        url = "https://example.com/test"
        req1 = create_request(url, referer="https://ref1.com")
        req2 = create_request(url, referer="https://ref2.com")
        
        assert req1.get_header('Referer') == "https://ref1.com"
        assert req2.get_header('Referer') == "https://ref2.com"
        
        # Both should have the same other headers
        assert req1.get_header('User-agent') == req2.get_header('User-agent')
        assert req1.get_header('Origin') == req2.get_header('Origin')
    
    def test_create_request_all_headers_present(self):
        """Test that all expected headers are present"""
        url = "https://example.com/test"
        req = create_request(url)
        
        expected_headers = [
            'User-agent',
            'Referer',
            'Origin',
            'Accept',
            'Accept-language'
        ]
        
        for header in expected_headers:
            assert req.get_header(header) is not None, f"Header {header} is missing"