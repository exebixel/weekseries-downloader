"""
Shared fixtures and configuration for tests
"""

import pytest
from unittest.mock import Mock, patch
from weekseries_downloader.models import EpisodeInfo, ExtractionResult, DownloadConfig


@pytest.fixture
def sample_episode_info():
    """Sample EpisodeInfo for testing"""
    return EpisodeInfo(
        series_name="the-good-doctor",
        season=1,
        episode=3,
        original_url="https://www.weekseries.info/series/the-good-doctor/temporada-1/episodio-03"
    )


@pytest.fixture
def sample_episode_info_with_special_chars():
    """EpisodeInfo with special characters in series name"""
    return EpisodeInfo(
        series_name="the/good<doctor>",
        season=2,
        episode=5,
        original_url="https://www.weekseries.info/series/the-good-doctor/temporada-2/episodio-05"
    )


@pytest.fixture
def successful_extraction_result():
    """Sample successful ExtractionResult"""
    return ExtractionResult(
        success=True,
        stream_url="https://example.com/stream.m3u8",
        referer_url="https://www.weekseries.info/",
        episode_info=EpisodeInfo(
            series_name="test-series",
            season=1,
            episode=1,
            original_url="https://www.weekseries.info/series/test-series/temporada-1/episodio-01"
        )
    )


@pytest.fixture
def failed_extraction_result():
    """Sample failed ExtractionResult"""
    return ExtractionResult(
        success=False,
        error_message="Streaming URL not found"
    )


@pytest.fixture
def sample_download_config():
    """Sample DownloadConfig for testing"""
    return DownloadConfig(
        stream_url="https://example.com/stream.m3u8",
        output_file="test_video.mp4",
        referer_url="https://www.weekseries.info/",
        convert_to_mp4=True
    )


@pytest.fixture
def sample_download_config_no_referer():
    """DownloadConfig without referer"""
    return DownloadConfig(
        stream_url="https://example.com/stream.m3u8",
        output_file="test_video.mp4",
        convert_to_mp4=False
    )


# URL fixtures for testing
@pytest.fixture
def valid_weekseries_urls():
    """List of valid weekseries.info URLs"""
    return [
        "https://www.weekseries.info/series/the-good-doctor/temporada-1/episodio-01",
        "http://www.weekseries.info/series/breaking-bad/temporada-5/episodio-16",
        "https://weekseries.info/series/game-of-thrones/temporada-8/episodio-06"
    ]


@pytest.fixture
def invalid_weekseries_urls():
    """List of invalid weekseries.info URLs"""
    return [
        "https://www.weekseries.info/series/the-good-doctor/temporada-1",  # Missing episode
        "https://www.weekseries.info/series/the-good-doctor/episodio-01",  # Missing season
        "https://example.com/series/the-good-doctor/temporada-1/episodio-01",  # Wrong domain
        "not-a-url",
        "",
        None
    ]


@pytest.fixture
def valid_stream_urls():
    """List of valid streaming URLs"""
    return [
        "https://example.com/stream.m3u8",
        "https://video.server.com/path/to/stream.m3u8",
        "https://cdn.example.com/hls/stream/index.m3u8"
    ]


@pytest.fixture
def valid_base64_urls():
    """List of valid base64 encoded URLs"""
    return [
        "aHR0cHM6Ly9leGFtcGxlLmNvbS9zdHJlYW0ubTN1OA==",  # https://example.com/stream.m3u8
        "aHR0cDovL3Rlc3QuY29tL3ZpZGVvLm0zdTg=",  # http://test.com/video.m3u8
    ]


@pytest.fixture
def invalid_base64_strings():
    """List of invalid base64 strings"""
    return [
        "invalid-base64!@#",
        "short",
        "",
        None,
        "almost-valid-but-not-quite"
    ]


# Mock fixtures
@pytest.fixture
def mock_http_response():
    """Mock HTTP response"""
    mock_response = Mock()
    mock_response.read.return_value = b'<html><script>var stream = "aHR0cHM6Ly9leGFtcGxlLmNvbS9zdHJlYW0ubTN1OA==";</script></html>'
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=None)
    return mock_response


@pytest.fixture
def mock_urlopen(mock_http_response):
    """Mock urllib.request.urlopen"""
    with patch('urllib.request.urlopen', return_value=mock_http_response) as mock:
        yield mock


@pytest.fixture
def mock_subprocess_success():
    """Mock successful subprocess.run"""
    with patch('subprocess.run') as mock:
        mock.return_value.returncode = 0
        yield mock


@pytest.fixture
def mock_subprocess_failure():
    """Mock failed subprocess.run"""
    with patch('subprocess.run') as mock:
        mock.side_effect = FileNotFoundError("ffmpeg not found")
        yield mock


@pytest.fixture
def mock_time():
    """Mock time.time for cache testing"""
    with patch('time.time', return_value=1000.0) as mock:
        yield mock


# Sample data fixtures
@pytest.fixture
def sample_m3u8_content():
    """Sample M3U8 playlist content"""
    return """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXTINF:10.0,
segment001.ts
#EXTINF:10.0,
segment002.ts
#EXTINF:10.0,
segment003.ts
#EXT-X-ENDLIST"""


@pytest.fixture
def sample_master_m3u8_content():
    """Sample master M3U8 playlist with multiple qualities"""
    return """#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=1280000,RESOLUTION=854x480
480p/index.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=2560000,RESOLUTION=1280x720
720p/index.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=5120000,RESOLUTION=1920x1080
1080p/index.m3u8"""


@pytest.fixture
def sample_html_with_base64():
    """Sample HTML content with base64 encoded URL"""
    return """
    <html>
    <head><title>Test Page</title></head>
    <body>
        <script>
            var videoUrl = "aHR0cHM6Ly9leGFtcGxlLmNvbS9zdHJlYW0ubTN1OA==";
            var player = initPlayer(videoUrl);
        </script>
    </body>
    </html>
    """


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_cache():
    """Automatically cleanup cache after each test"""
    yield
    # Import here to avoid circular imports
    from weekseries_downloader.cache import clear_url_cache
    clear_url_cache()