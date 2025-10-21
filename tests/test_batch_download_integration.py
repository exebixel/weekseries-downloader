"""
Integration tests for batch download functionality
"""

import os
import pytest
from pathlib import Path
from unittest.mock import Mock
from weekseries_downloader.series_processing import SeriesParser, BatchDownloader
from weekseries_downloader.models import (
    BatchDownloadConfig,
    ExtractionResult,
    EpisodeInfo,
)


class TestBatchDownloadIntegration:
    """Integration tests for SeriesParser + BatchDownloader workflow"""

    @pytest.fixture
    def series_html(self):
        """HTML with 5 episodes across 2 seasons"""
        return """
        <html>
            <body>
                <a href="/series/test-show/temporada-1/episodio-01">S01E01</a>
                <a href="/series/test-show/temporada-1/episodio-02">S01E02</a>
                <a href="/series/test-show/temporada-1/episodio-03">S01E03</a>
                <a href="/series/test-show/temporada-2/episodio-01">S02E01</a>
                <a href="/series/test-show/temporada-2/episodio-02">S02E02</a>
            </body>
        </html>
        """

    @pytest.fixture
    def mock_http_client(self, series_html):
        """Mock HTTP client that returns series HTML"""
        mock = Mock()
        mock.fetch.return_value = series_html
        return mock

    @pytest.fixture
    def mock_url_extractor(self):
        """Mock URL extractor that returns successful results"""
        mock = Mock()
        mock.extract_stream_url.return_value = ExtractionResult(
            success=True,
            stream_url="https://example.com/stream.m3u8",
            referer_url="https://www.weekseries.info",
            episode_info=EpisodeInfo(series_name="test-show", season=1, episode=1, original_url="test"),
        )
        return mock

    @pytest.fixture
    def mock_hls_downloader(self):
        """Mock HLS downloader that always succeeds"""
        mock = Mock()
        mock.download.return_value = True
        return mock

    @pytest.fixture
    def temp_output_dir(self, tmp_path):
        """Create temporary output directory"""
        output_dir = tmp_path / "downloads"
        output_dir.mkdir()
        return str(output_dir)

    def test_full_series_download_workflow(self, mock_http_client, mock_url_extractor, mock_hls_downloader, temp_output_dir):
        """Test complete workflow: parse series -> download all episodes"""
        series_url = "https://www.weekseries.info/series/test-show"

        # Parse series page
        parser = SeriesParser(http_client=mock_http_client)
        series_info = parser.parse_series_page(series_url)

        assert series_info.total_episodes == 5
        assert len(series_info.seasons) == 2

        # Create download configuration
        config = BatchDownloadConfig(
            series_info=series_info, season_filter=None, output_dir=temp_output_dir, convert_to_mp4=False, continue_on_error=True
        )

        # Download series
        batch_downloader = BatchDownloader(url_extractor=mock_url_extractor, hls_downloader=mock_hls_downloader)
        result = batch_downloader.download_series(config)

        # Verify results
        assert result.total_episodes == 5
        assert result.successful == 5
        assert result.failed == 0
        assert result.skipped == 0
        assert len(result.results) == 5

        # Verify all episodes were attempted
        assert mock_url_extractor.extract_stream_url.call_count == 5
        assert mock_hls_downloader.download.call_count == 5

    def test_season_filtering(self, mock_http_client, mock_url_extractor, mock_hls_downloader, temp_output_dir):
        """Test downloading only a specific season"""
        series_url = "https://www.weekseries.info/series/test-show"

        # Parse series page
        parser = SeriesParser(http_client=mock_http_client)
        series_info = parser.parse_series_page(series_url)

        # Download only season 1
        config = BatchDownloadConfig(
            series_info=series_info, season_filter=1, output_dir=temp_output_dir, convert_to_mp4=False, continue_on_error=True
        )

        batch_downloader = BatchDownloader(url_extractor=mock_url_extractor, hls_downloader=mock_hls_downloader)
        result = batch_downloader.download_series(config)

        # Should only download 3 episodes from season 1
        assert result.total_episodes == 3
        assert result.successful == 3
        assert mock_hls_downloader.download.call_count == 3

    def test_continue_on_error_behavior(self, mock_http_client, mock_url_extractor, mock_hls_downloader, temp_output_dir):
        """Test that download continues when one episode fails"""
        series_url = "https://www.weekseries.info/series/test-show"

        # Configure extractor to fail on specific episode (S01E02 only)
        def extract_side_effect(url):
            if "temporada-1/episodio-02" in url:
                return ExtractionResult(success=False, error_message="Failed to extract")
            return ExtractionResult(
                success=True,
                stream_url="https://example.com/stream.m3u8",
                referer_url="https://www.weekseries.info",
            )

        mock_url_extractor.extract_stream_url.side_effect = extract_side_effect

        # Parse and download
        parser = SeriesParser(http_client=mock_http_client)
        series_info = parser.parse_series_page(series_url)

        config = BatchDownloadConfig(
            series_info=series_info, season_filter=None, output_dir=temp_output_dir, convert_to_mp4=False, continue_on_error=True
        )

        batch_downloader = BatchDownloader(url_extractor=mock_url_extractor, hls_downloader=mock_hls_downloader)
        result = batch_downloader.download_series(config)

        # Should have 4 successes and 1 failure
        assert result.total_episodes == 5
        assert result.successful == 4
        assert result.failed == 1
        assert mock_hls_downloader.download.call_count == 4  # Only called for successful extractions

    def test_stop_on_error_behavior(self, mock_http_client, mock_url_extractor, mock_hls_downloader, temp_output_dir):
        """Test that download stops when error occurs and continue_on_error=False"""
        series_url = "https://www.weekseries.info/series/test-show"

        # Configure extractor to fail on specific episode (S01E02 only)
        def extract_side_effect(url):
            if "temporada-1/episodio-02" in url:
                return ExtractionResult(success=False, error_message="Failed to extract")
            return ExtractionResult(
                success=True,
                stream_url="https://example.com/stream.m3u8",
                referer_url="https://www.weekseries.info",
            )

        mock_url_extractor.extract_stream_url.side_effect = extract_side_effect

        # Parse and download
        parser = SeriesParser(http_client=mock_http_client)
        series_info = parser.parse_series_page(series_url)

        config = BatchDownloadConfig(
            series_info=series_info,
            season_filter=None,
            output_dir=temp_output_dir,
            convert_to_mp4=False,
            continue_on_error=False,  # Stop on error
        )

        batch_downloader = BatchDownloader(url_extractor=mock_url_extractor, hls_downloader=mock_hls_downloader)
        result = batch_downloader.download_series(config)

        # Should stop after first failure (second episode)
        assert result.total_episodes == 5
        assert result.successful == 1  # Only first episode
        assert result.failed == 1  # Second episode
        assert len(result.results) == 2  # Only processed 2 episodes

    def test_skip_existing_files(self, mock_http_client, mock_url_extractor, mock_hls_downloader, temp_output_dir):
        """Test that existing files are skipped"""
        series_url = "https://www.weekseries.info/series/test-show"

        # Create some existing files
        existing_file = Path(temp_output_dir) / "test_show_S01E01.ts"
        existing_file.write_text("existing content")

        # Parse and download
        parser = SeriesParser(http_client=mock_http_client)
        series_info = parser.parse_series_page(series_url)

        config = BatchDownloadConfig(
            series_info=series_info, season_filter=None, output_dir=temp_output_dir, convert_to_mp4=False, continue_on_error=True
        )

        batch_downloader = BatchDownloader(url_extractor=mock_url_extractor, hls_downloader=mock_hls_downloader)
        result = batch_downloader.download_series(config)

        # Should skip 1 file, download 4 new ones
        assert result.successful == 4
        assert result.skipped == 1
        assert mock_hls_downloader.download.call_count == 4

    def test_convert_to_mp4_option(self, mock_http_client, mock_url_extractor, mock_hls_downloader, temp_output_dir):
        """Test that convert_to_mp4 flag is passed correctly"""
        series_url = "https://www.weekseries.info/series/test-show"

        # Parse series
        parser = SeriesParser(http_client=mock_http_client)
        series_info = parser.parse_series_page(series_url)

        # Download with MP4 conversion
        config = BatchDownloadConfig(
            series_info=series_info,
            season_filter=None,
            output_dir=temp_output_dir,
            convert_to_mp4=True,  # Enable conversion
            continue_on_error=True,
        )

        batch_downloader = BatchDownloader(url_extractor=mock_url_extractor, hls_downloader=mock_hls_downloader)
        _ = batch_downloader.download_series(config)

        # Verify conversion flag was passed
        for call in mock_hls_downloader.download.call_args_list:
            assert call.kwargs["convert_to_mp4"] is True

    def test_output_directory_creation(self, mock_http_client, mock_url_extractor, mock_hls_downloader, tmp_path):
        """Test that output directory is created if it doesn't exist"""
        series_url = "https://www.weekseries.info/series/test-show"
        output_dir = str(tmp_path / "new" / "nested" / "directory")

        # Parse series
        parser = SeriesParser(http_client=mock_http_client)
        series_info = parser.parse_series_page(series_url)

        # Download to non-existent directory
        config = BatchDownloadConfig(series_info=series_info, season_filter=None, output_dir=output_dir, convert_to_mp4=False, continue_on_error=True)

        batch_downloader = BatchDownloader(url_extractor=mock_url_extractor, hls_downloader=mock_hls_downloader)
        result = batch_downloader.download_series(config)

        # Verify directory was created
        assert os.path.exists(output_dir)
        assert result.successful == 5

    def test_filename_generation(self, mock_http_client, mock_url_extractor, mock_hls_downloader, temp_output_dir):
        """Test that filenames are generated correctly"""
        series_url = "https://www.weekseries.info/series/test-show"

        # Parse series
        parser = SeriesParser(http_client=mock_http_client)
        series_info = parser.parse_series_page(series_url)

        # Download with .ts extension
        config = BatchDownloadConfig(
            series_info=series_info, season_filter=1, output_dir=temp_output_dir, convert_to_mp4=False, continue_on_error=True
        )

        batch_downloader = BatchDownloader(url_extractor=mock_url_extractor, hls_downloader=mock_hls_downloader)
        _ = batch_downloader.download_series(config)

        # Check that correct filenames were passed to downloader
        expected_files = [
            "test_show_S01E01.ts",
            "test_show_S01E02.ts",
            "test_show_S01E03.ts",
        ]

        for i, call in enumerate(mock_hls_downloader.download.call_args_list):
            output_path = call.kwargs["output_path"]
            assert output_path.name == expected_files[i]

    def test_empty_series(self, mock_http_client):
        """Test handling of series with no episodes"""
        series_url = "https://www.weekseries.info/series/empty-show"

        # Mock empty HTML
        mock_http_client.fetch.return_value = "<html><body></body></html>"

        # Should raise error when parsing
        parser = SeriesParser(http_client=mock_http_client)
        with pytest.raises(Exception):  # SeriesParsingError
            parser.parse_series_page(series_url)

    def test_nonexistent_season_filter(self, mock_http_client, temp_output_dir):
        """Test filtering by a season that doesn't exist"""
        series_url = "https://www.weekseries.info/series/test-show"

        # Parse series
        parser = SeriesParser(http_client=mock_http_client)
        series_info = parser.parse_series_page(series_url)

        # Try to download season 99 (doesn't exist)
        config = BatchDownloadConfig(
            series_info=series_info, season_filter=99, output_dir=temp_output_dir, convert_to_mp4=False, continue_on_error=True
        )

        batch_downloader = BatchDownloader.create_default()
        result = batch_downloader.download_series(config)

        # Should have no episodes
        assert result.total_episodes == 0
        assert result.successful == 0
