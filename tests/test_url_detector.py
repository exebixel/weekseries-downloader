"""
Tests for weekseries_downloader.url_processing.url_parser module
"""

from weekseries_downloader.url_processing import URLParser, URLType


class TestDetectUrlType:
    """Tests for detect_url_type function"""

    def test_detect_weekseries_url_type(self, valid_weekseries_urls):
        """Test detect_url_type with valid weekseries URLs"""
        for url in valid_weekseries_urls:
            result = URLParser.detect_url_type(url)
            assert result == URLType.WEEKSERIES

    def test_detect_stream_url_type(self, valid_stream_urls):
        """Test detect_url_type with valid streaming URLs"""
        for url in valid_stream_urls:
            result = URLParser.detect_url_type(url)
            assert result == URLType.DIRECT_STREAM

    def test_detect_base64_url_type(self, valid_base64_urls):
        """Test detect_url_type with valid base64 strings"""
        for base64_string in valid_base64_urls:
            result = URLParser.detect_url_type(base64_string)
            assert result == URLType.BASE64

    def test_detect_unknown_url_type(self, invalid_weekseries_urls):
        """Test detect_url_type with invalid/unknown URLs"""
        for url in invalid_weekseries_urls:
            result = URLParser.detect_url_type(url)
            assert result == URLType.UNKNOWN

    def test_detect_url_type_edge_cases(self):
        """Test detect_url_type with edge cases and various formats"""
        test_cases = [
            # Edge cases
            ("", URLType.UNKNOWN),
            (None, URLType.UNKNOWN),
            ("not-a-url", URLType.UNKNOWN),
            ("https://other-site.com/video", URLType.UNKNOWN),
            # Valid formats
            ("https://www.weekseries.info/series/test/temporada-1/episodio-01", URLType.WEEKSERIES),
            ("https://example.com/video.m3u8", URLType.DIRECT_STREAM),
            ("https://cdn.example.com/stream/playlist.m3u8", URLType.DIRECT_STREAM),
            ("aHR0cHM6Ly9leGFtcGxlLmNvbS9zdHJlYW0ubTN1OA==", URLType.BASE64),
        ]

        for url, expected_type in test_cases:
            result = URLParser.detect_url_type(url)
            assert result == expected_type, f"Failed for URL: {url}"


class TestValidateWeekseriesUrl:
    """Tests for validate_weekseries_url function"""

    def test_validate_weekseries_url_valid(self, valid_weekseries_urls):
        """Test validate_weekseries_url with valid URLs"""
        for url in valid_weekseries_urls:
            result = URLParser.is_weekseries_url(url)
            assert result is True

    def test_validate_weekseries_url_invalid(self, invalid_weekseries_urls):
        """Test validate_weekseries_url with invalid URLs"""
        for url in invalid_weekseries_urls:
            result = URLParser.is_weekseries_url(url)
            assert result is False

    def test_validate_weekseries_url_malformed_patterns(self):
        """Test validate_weekseries_url with malformed patterns"""
        malformed_urls = [
            "https://www.weekseries.info/series/test/temporada-1",  # Missing episode
            "https://www.weekseries.info/series/test/episodio-01",  # Missing season
            "https://www.weekseries.info/series/temporada-1/episodio-01",  # Missing series name
            "https://www.weekseries.info/series/test/temporada-abc/episodio-01",  # Non-numeric season
            "https://www.weekseries.info/series/test/temporada-1/episodio-abc",  # Non-numeric episode
            "https://www.weekseries.info/series/test/season-1/episode-01",  # Wrong keywords
        ]

        for url in malformed_urls:
            result = URLParser.is_weekseries_url(url)
            assert result is False, f"Should be invalid: {url}"

    def test_validate_weekseries_url_edge_cases_and_protocols(self):
        """Test validate_weekseries_url with edge cases and different protocols"""
        test_cases = [
            # Edge cases
            ("", False),
            (None, False),
            ("https://", False),
            ("https://weekseries.info", False),
            ("https://www.weekseries.info/", False),
            ("https://www.weekseries.info/series/", False),
            # Different protocols
            ("https://www.weekseries.info/series/test/temporada-1/episodio-01", True),
            ("http://www.weekseries.info/series/test/temporada-1/episodio-01", True),
            ("https://weekseries.info/series/test/temporada-1/episodio-01", True),
            ("ftp://www.weekseries.info/series/test/temporada-1/episodio-01", False),
            ("www.weekseries.info/series/test/temporada-1/episodio-01", False),  # No protocol
        ]

        for url, expected in test_cases:
            result = URLParser.is_weekseries_url(url)
            assert result == expected, f"Failed for URL: {url}"


class TestIsStreamUrl:
    """Tests for is_stream_url function"""

    def test_is_stream_url_valid(self, valid_stream_urls):
        """Test is_stream_url with valid streaming URLs"""
        for url in valid_stream_urls:
            result = URLParser.is_direct_stream_url(url)
            assert result is True

    def test_is_stream_url_m3u8_extension(self):
        """Test is_stream_url with .m3u8 extension"""
        m3u8_urls = [
            "https://example.com/video.m3u8",
            "http://cdn.example.com/stream/playlist.m3u8",
            "https://video.server.com/hls/index.m3u8",
        ]

        for url in m3u8_urls:
            result = URLParser.is_direct_stream_url(url)
            assert result is True

    def test_is_stream_url_stream_keyword(self):
        """Test is_stream_url with 'stream' keyword"""
        stream_urls = [
            "https://example.com/stream",
            "https://example.com/video/stream/index",
            "https://streaming.example.com/video",
            "https://example.com/STREAM",  # Case insensitive
        ]

        for url in stream_urls:
            result = URLParser.is_direct_stream_url(url)
            assert result is True

    def test_is_stream_url_invalid_and_edge_cases(self):
        """Test is_stream_url with invalid URLs and edge cases"""
        test_cases = [
            # Invalid URLs
            ("", False),
            (None, False),
            ("not-a-url", False),
            ("https://example.com/video.mp4", False),
            ("https://example.com/page.html", False),
            ("ftp://example.com/stream.m3u8", False),  # Wrong protocol
            ("example.com/stream.m3u8", False),  # No protocol
            # Edge cases
            ("https://", False),
            ("http://", False),
            ("https://example.com", False),
            ("https://example.com/", False),
        ]

        for url, expected in test_cases:
            result = URLParser.is_direct_stream_url(url)
            assert result == expected, f"Failed for URL: {url}"


class TestIsBase64String:
    """Tests for is_base64_string function"""

    def test_is_base64_string_valid(self, valid_base64_urls):
        """Test is_base64_string with valid base64 strings"""
        for base64_string in valid_base64_urls:
            result = URLParser.is_base64_encoded(base64_string)
            assert result is True

    def test_is_base64_string_invalid(self, invalid_base64_strings):
        """Test is_base64_string with invalid base64 strings"""
        for invalid_string in invalid_base64_strings:
            result = URLParser.is_base64_encoded(invalid_string)
            # The function only checks pattern, not actual base64 validity
            if invalid_string is None or invalid_string == "" or len(invalid_string) < 4:
                assert result is False
            elif invalid_string == "short":  # Length 5, valid pattern
                assert result is True
            elif "!" in invalid_string or "@" in invalid_string or "#" in invalid_string:
                assert result is False  # Invalid characters
            else:
                # For other cases, check if it matches the pattern
                import re

                expected = bool(re.match(r"^[A-Za-z0-9+/]*={0,2}$", invalid_string)) and len(invalid_string) >= 4
                assert result == expected

    def test_is_base64_string_valid_patterns(self):
        """Test is_base64_string with various valid base64 patterns"""
        valid_patterns = [
            "YWJjZA==",  # "abcd"
            "dGVzdA==",  # "test"
            "aGVsbG8gd29ybGQ=",  # "hello world"
            "MTIzNDU2Nzg5MA==",  # "1234567890"
            "QWJDZEVmR2hJams=",  # Mixed case
        ]

        for pattern in valid_patterns:
            result = URLParser.is_base64_encoded(pattern)
            assert result is True, f"Should be valid base64: {pattern}"

    def test_is_base64_string_invalid_patterns(self):
        """Test is_base64_string with invalid patterns"""
        invalid_patterns = [
            "abc!@#",  # Invalid characters
            "abc",  # Too short
            "ab",  # Too short
            "a",  # Too short
            "",  # Empty
            None,  # None
            "abc===",  # Too much padding
            "abc=d=",  # Padding in wrong place
        ]

        for pattern in invalid_patterns:
            result = URLParser.is_base64_encoded(pattern)
            assert result is False, f"Should be invalid base64: {pattern}"

    def test_is_base64_string_length_requirements(self):
        """Test is_base64_string length requirements"""
        # Minimum length should be 4
        assert URLParser.is_base64_encoded("abc") is False  # Length 3
        assert URLParser.is_base64_encoded("abcd") is True  # Length 4
        assert URLParser.is_base64_encoded("abcde") is True  # Length 5 (valid pattern, function doesn't check multiples of 4)
        assert URLParser.is_base64_encoded("abcdefgh") is True  # Length 8


class TestExtractEpisodeInfo:
    """Tests for extract_episode_info function"""

    def test_extract_episode_info_valid(self):
        """Test extract_episode_info with valid weekseries URLs"""
        # Test first URL: the-good-doctor, season 1, episode 1
        url = "https://www.weekseries.info/series/the-good-doctor/temporada-1/episodio-01"
        result = URLParser.extract_episode_info(url)

        assert result is not None
        assert result.series_name == "the-good-doctor"
        assert result.season == 1
        assert result.episode == 1
        assert result.original_url == url

    def test_extract_episode_info_different_numbers(self):
        """Test extract_episode_info with different season/episode numbers"""
        test_cases = [
            ("https://www.weekseries.info/series/breaking-bad/temporada-5/episodio-16", "breaking-bad", 5, 16),
            ("https://www.weekseries.info/series/game-of-thrones/temporada-8/episodio-06", "game-of-thrones", 8, 6),
            ("https://www.weekseries.info/series/test-series/temporada-10/episodio-25", "test-series", 10, 25),
        ]

        for url, expected_series, expected_season, expected_episode in test_cases:
            result = URLParser.extract_episode_info(url)

            assert result is not None
            assert result.series_name == expected_series
            assert result.season == expected_season
            assert result.episode == expected_episode
            assert result.original_url == url

    def test_extract_episode_info_invalid_urls(self, invalid_weekseries_urls):
        """Test extract_episode_info with invalid URLs"""
        for url in invalid_weekseries_urls:
            result = URLParser.extract_episode_info(url)
            assert result is None

    def test_extract_episode_info_malformed_urls(self):
        """Test extract_episode_info with malformed URLs"""
        malformed_urls = [
            "https://www.weekseries.info/series/test/temporada-1",  # Missing episode
            "https://www.weekseries.info/series/test/episodio-01",  # Missing season
            "https://example.com/series/test/temporada-1/episodio-01",  # Wrong domain
        ]

        for url in malformed_urls:
            result = URLParser.extract_episode_info(url)
            assert result is None


    def test_extract_episode_info_series_name_formats(self):
        """Test extract_episode_info with different series name formats"""
        test_cases = [
            ("https://www.weekseries.info/series/the-good-doctor/temporada-1/episodio-01", "the-good-doctor"),
            ("https://www.weekseries.info/series/game-of-thrones/temporada-1/episodio-01", "game-of-thrones"),
            ("https://www.weekseries.info/series/simple/temporada-1/episodio-01", "simple"),
            (
                "https://www.weekseries.info/series/very-long-series-name-with-many-words/temporada-1/episodio-01",
                "very-long-series-name-with-many-words",
            ),
        ]

        for url, expected_series in test_cases:
            result = URLParser.extract_episode_info(url)

            assert result is not None
            assert result.series_name == expected_series


class TestIsSeriesUrl:
    """Tests for is_series_url function"""

    def test_is_series_url_valid(self):
        """Test is_series_url with valid series URLs"""
        valid_series_urls = [
            "https://www.weekseries.info/series/the-good-doctor",
            "https://www.weekseries.info/series/the-good-doctor/",
            "http://www.weekseries.info/series/mob-psycho-100-ii-dublado",
            "https://weekseries.info/series/breaking-bad",
            "https://weekseries.info/series/game-of-thrones/",
        ]

        for url in valid_series_urls:
            result = URLParser.is_series_url(url)
            assert result is True, f"Should be valid series URL: {url}"

    def test_is_series_url_invalid_episode_urls(self):
        """Test is_series_url returns False for episode URLs"""
        episode_urls = [
            "https://www.weekseries.info/series/the-good-doctor/temporada-1/episodio-01",
            "https://www.weekseries.info/series/breaking-bad/temporada-5/episodio-16",
            "http://weekseries.info/series/test/temporada-1/episodio-01",
        ]

        for url in episode_urls:
            result = URLParser.is_series_url(url)
            assert result is False, f"Should not be series URL (is episode): {url}"

    def test_is_series_url_invalid_urls(self):
        """Test is_series_url with invalid URLs"""
        invalid_urls = [
            "",
            None,
            "not-a-url",
            "https://other-site.com/series/test",
            "www.weekseries.info/series/test",  # No protocol
            "ftp://www.weekseries.info/series/test",  # Wrong protocol
            "https://www.weekseries.info/",  # Missing series path
            "https://www.weekseries.info/series/",  # Missing series name
        ]

        for url in invalid_urls:
            result = URLParser.is_series_url(url)
            assert result is False, f"Should be invalid series URL: {url}"

    def test_is_series_url_edge_cases(self):
        """Test is_series_url with edge cases"""
        test_cases = [
            ("https://www.weekseries.info/series/simple", True),
            ("https://www.weekseries.info/series/a", True),
            ("https://www.weekseries.info/series/test-series-123", True),
            ("https://www.weekseries.info/series/test/extra", False),  # Extra path component
            ("https://www.weekseries.info/series/test/temporada-1", False),  # Incomplete episode URL
        ]

        for url, expected in test_cases:
            result = URLParser.is_series_url(url)
            assert result == expected, f"Failed for URL: {url}"


class TestExtractSeriesName:
    """Tests for extract_series_name function"""

    def test_extract_series_name_valid(self):
        """Test extract_series_name with valid series URLs"""
        test_cases = [
            ("https://www.weekseries.info/series/the-good-doctor", "the-good-doctor"),
            ("https://www.weekseries.info/series/the-good-doctor/", "the-good-doctor"),
            ("https://www.weekseries.info/series/mob-psycho-100-ii-dublado", "mob-psycho-100-ii-dublado"),
            ("https://weekseries.info/series/breaking-bad", "breaking-bad"),
            ("http://www.weekseries.info/series/game-of-thrones/", "game-of-thrones"),
        ]

        for url, expected_name in test_cases:
            result = URLParser.extract_series_name(url)
            assert result == expected_name, f"Failed for URL: {url}"

    def test_extract_series_name_invalid(self):
        """Test extract_series_name with invalid URLs"""
        invalid_urls = [
            "",
            None,
            "not-a-url",
            "https://other-site.com/series/test",
            "https://www.weekseries.info/series/test/temporada-1/episodio-01",  # Episode URL
            "https://www.weekseries.info/",  # No series path
            "www.weekseries.info/series/test",  # No protocol
        ]

        for url in invalid_urls:
            result = URLParser.extract_series_name(url)
            assert result is None, f"Should return None for invalid URL: {url}"

    def test_extract_series_name_various_formats(self):
        """Test extract_series_name with various series name formats"""
        test_cases = [
            ("https://www.weekseries.info/series/simple", "simple"),
            ("https://www.weekseries.info/series/a", "a"),
            ("https://www.weekseries.info/series/test-123", "test-123"),
            ("https://www.weekseries.info/series/very-long-series-name-with-many-words", "very-long-series-name-with-many-words"),
        ]

        for url, expected_name in test_cases:
            result = URLParser.extract_series_name(url)
            assert result == expected_name, f"Failed for URL: {url}"


class TestDetectUrlTypeSeries:
    """Tests for detect_url_type with series URLs"""

    def test_detect_series_url_type(self):
        """Test detect_url_type correctly identifies series URLs"""
        series_urls = [
            "https://www.weekseries.info/series/the-good-doctor",
            "https://www.weekseries.info/series/the-good-doctor/",
            "http://www.weekseries.info/series/mob-psycho-100-ii-dublado",
            "https://weekseries.info/series/breaking-bad",
        ]

        for url in series_urls:
            result = URLParser.detect_url_type(url)
            assert result == URLType.SERIES, f"Failed for series URL: {url}"

    def test_detect_url_type_prioritizes_series_over_episode(self):
        """Test that series URLs are detected before episode URLs"""
        # Series URL should be detected as SERIES, not WEEKSERIES
        url = "https://www.weekseries.info/series/the-good-doctor"
        result = URLParser.detect_url_type(url)
        assert result == URLType.SERIES

        # Episode URL should still be detected as WEEKSERIES
        url = "https://www.weekseries.info/series/the-good-doctor/temporada-1/episodio-01"
        result = URLParser.detect_url_type(url)
        assert result == URLType.WEEKSERIES

    def test_detect_url_type_comprehensive(self):
        """Comprehensive test for detect_url_type with all URL types"""
        test_cases = [
            # Series URLs
            ("https://www.weekseries.info/series/test", URLType.SERIES),
            ("https://www.weekseries.info/series/test/", URLType.SERIES),
            # Episode URLs
            ("https://www.weekseries.info/series/test/temporada-1/episodio-01", URLType.WEEKSERIES),
            # Stream URLs
            ("https://example.com/video.m3u8", URLType.DIRECT_STREAM),
            # Base64
            ("aHR0cHM6Ly9leGFtcGxlLmNvbQ==", URLType.BASE64),
            # Unknown
            ("", URLType.UNKNOWN),
            (None, URLType.UNKNOWN),
            ("https://other-site.com/video", URLType.UNKNOWN),
        ]

        for url, expected_type in test_cases:
            result = URLParser.detect_url_type(url)
            assert result == expected_type, f"Failed for URL: {url}"
