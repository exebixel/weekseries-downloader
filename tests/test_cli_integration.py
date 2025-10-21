"""
Integration tests for CLI series download functionality
"""

import pytest
from unittest.mock import Mock, patch
from click.testing import CliRunner
from weekseries_downloader.cli import main
from weekseries_downloader.models import SeriesInfo, EpisodeLink, BatchDownloadResult


class TestCLISeriesDownload:
    """Integration tests for CLI series download"""

    @pytest.fixture
    def cli_runner(self):
        """Create Click test runner"""
        return CliRunner()

    @pytest.fixture
    def mock_series_info(self):
        """Create mock SeriesInfo"""
        episodes_s1 = [
            EpisodeLink(
                url="/series/test/temporada-1/episodio-01",
                season=1,
                episode=1,
                full_url="https://weekseries.info/series/test/temporada-1/episodio-01",
            ),
            EpisodeLink(
                url="/series/test/temporada-1/episodio-02",
                season=1,
                episode=2,
                full_url="https://weekseries.info/series/test/temporada-1/episodio-02",
            ),
        ]
        episodes_s2 = [
            EpisodeLink(
                url="/series/test/temporada-2/episodio-01",
                season=2,
                episode=1,
                full_url="https://weekseries.info/series/test/temporada-2/episodio-01",
            ),
        ]

        return SeriesInfo(
            series_name="test-series",
            series_url="https://www.weekseries.info/series/test-series",
            total_episodes=3,
            seasons={1: episodes_s1, 2: episodes_s2},
        )

    @pytest.fixture
    def mock_batch_result_success(self):
        """Create successful batch download result"""
        return BatchDownloadResult(total_episodes=3, successful=3, failed=0, skipped=0, results=[], total_duration_seconds=10.0)

    def test_series_url_detection_and_routing(self, cli_runner, mock_series_info, mock_batch_result_success):
        """Test that series URLs are detected and routed to series download handler"""
        with patch("weekseries_downloader.cli.SeriesParser") as mock_parser_class, patch(
            "weekseries_downloader.cli.BatchDownloader"
        ) as mock_downloader_class:
            # Configure mocks
            mock_parser = Mock()
            mock_parser.parse_series_page.return_value = mock_series_info
            mock_parser_class.create_default.return_value = mock_parser

            mock_downloader = Mock()
            mock_downloader.download_series.return_value = mock_batch_result_success
            mock_downloader_class.create_default.return_value = mock_downloader

            # Run CLI with series URL
            result = cli_runner.invoke(main, ["--url", "https://www.weekseries.info/series/test-series"])

            # Verify series download was triggered
            assert result.exit_code == 0
            mock_parser.parse_series_page.assert_called_once()
            mock_downloader.download_series.assert_called_once()

    def test_series_download_with_season_filter(self, cli_runner, mock_series_info, mock_batch_result_success):
        """Test --season option is passed correctly"""
        with patch("weekseries_downloader.cli.SeriesParser") as mock_parser_class, patch(
            "weekseries_downloader.cli.BatchDownloader"
        ) as mock_downloader_class:
            # Configure mocks
            mock_parser = Mock()
            mock_parser.parse_series_page.return_value = mock_series_info
            mock_parser_class.create_default.return_value = mock_parser

            mock_downloader = Mock()
            mock_downloader.download_series.return_value = mock_batch_result_success
            mock_downloader_class.create_default.return_value = mock_downloader

            # Run CLI with season filter
            result = cli_runner.invoke(main, ["--url", "https://www.weekseries.info/series/test-series", "--season", "1"])

            # Verify season filter was passed in config
            assert result.exit_code == 0
            config = mock_downloader.download_series.call_args[0][0]
            assert config.season_filter == 1

    def test_series_download_with_custom_output_dir(self, cli_runner, mock_series_info, mock_batch_result_success):
        """Test --output-dir option is used"""
        with patch("weekseries_downloader.cli.SeriesParser") as mock_parser_class, patch(
            "weekseries_downloader.cli.BatchDownloader"
        ) as mock_downloader_class:
            # Configure mocks
            mock_parser = Mock()
            mock_parser.parse_series_page.return_value = mock_series_info
            mock_parser_class.create_default.return_value = mock_parser

            mock_downloader = Mock()
            mock_downloader.download_series.return_value = mock_batch_result_success
            mock_downloader_class.create_default.return_value = mock_downloader

            # Run CLI with custom output directory
            result = cli_runner.invoke(main, ["--url", "https://www.weekseries.info/series/test-series", "--output-dir", "/custom/path"])

            # Verify custom output dir was used
            assert result.exit_code == 0
            config = mock_downloader.download_series.call_args[0][0]
            assert config.output_dir == "/custom/path"

    def test_series_download_default_output_dir(self, cli_runner, mock_series_info, mock_batch_result_success):
        """Test default output directory is based on series name"""
        with patch("weekseries_downloader.cli.SeriesParser") as mock_parser_class, patch(
            "weekseries_downloader.cli.BatchDownloader"
        ) as mock_downloader_class:
            # Configure mocks
            mock_parser = Mock()
            mock_parser.parse_series_page.return_value = mock_series_info
            mock_parser_class.create_default.return_value = mock_parser

            mock_downloader = Mock()
            mock_downloader.download_series.return_value = mock_batch_result_success
            mock_downloader_class.create_default.return_value = mock_downloader

            # Run CLI without output-dir option
            result = cli_runner.invoke(main, ["--url", "https://www.weekseries.info/series/test-series"])

            # Verify default output dir is series name
            assert result.exit_code == 0
            config = mock_downloader.download_series.call_args[0][0]
            assert config.output_dir == "./test-series"

    def test_series_download_with_no_convert(self, cli_runner, mock_series_info, mock_batch_result_success):
        """Test --no-convert option is passed correctly"""
        with patch("weekseries_downloader.cli.SeriesParser") as mock_parser_class, patch(
            "weekseries_downloader.cli.BatchDownloader"
        ) as mock_downloader_class:
            # Configure mocks
            mock_parser = Mock()
            mock_parser.parse_series_page.return_value = mock_series_info
            mock_parser_class.create_default.return_value = mock_parser

            mock_downloader = Mock()
            mock_downloader.download_series.return_value = mock_batch_result_success
            mock_downloader_class.create_default.return_value = mock_downloader

            # Run CLI with --no-convert
            result = cli_runner.invoke(main, ["--url", "https://www.weekseries.info/series/test-series", "--no-convert"])

            # Verify convert_to_mp4 is False
            assert result.exit_code == 0
            config = mock_downloader.download_series.call_args[0][0]
            assert config.convert_to_mp4 is False

    def test_series_download_with_stop_on_error(self, cli_runner, mock_series_info, mock_batch_result_success):
        """Test --stop-on-error option is passed correctly"""
        with patch("weekseries_downloader.cli.SeriesParser") as mock_parser_class, patch(
            "weekseries_downloader.cli.BatchDownloader"
        ) as mock_downloader_class:
            # Configure mocks
            mock_parser = Mock()
            mock_parser.parse_series_page.return_value = mock_series_info
            mock_parser_class.create_default.return_value = mock_parser

            mock_downloader = Mock()
            mock_downloader.download_series.return_value = mock_batch_result_success
            mock_downloader_class.create_default.return_value = mock_downloader

            # Run CLI with --stop-on-error
            result = cli_runner.invoke(main, ["--url", "https://www.weekseries.info/series/test-series", "--stop-on-error"])

            # Verify continue_on_error is False
            assert result.exit_code == 0
            config = mock_downloader.download_series.call_args[0][0]
            assert config.continue_on_error is False

    def test_series_download_failure_exit_code(self, cli_runner, mock_series_info):
        """Test that CLI exits with code 1 when all downloads fail"""
        with patch("weekseries_downloader.cli.SeriesParser") as mock_parser_class, patch(
            "weekseries_downloader.cli.BatchDownloader"
        ) as mock_downloader_class:
            # Configure mocks
            mock_parser = Mock()
            mock_parser.parse_series_page.return_value = mock_series_info
            mock_parser_class.create_default.return_value = mock_parser

            mock_downloader = Mock()
            # All downloads failed
            mock_downloader.download_series.return_value = BatchDownloadResult(
                total_episodes=3, successful=0, failed=3, skipped=0, results=[], total_duration_seconds=5.0
            )
            mock_downloader_class.create_default.return_value = mock_downloader

            # Run CLI
            result = cli_runner.invoke(main, ["--url", "https://www.weekseries.info/series/test-series"])

            # Should exit with error code
            assert result.exit_code == 1

    def test_series_download_partial_success_exit_code(self, cli_runner, mock_series_info):
        """Test that CLI exits with code 0 when at least one download succeeds"""
        with patch("weekseries_downloader.cli.SeriesParser") as mock_parser_class, patch(
            "weekseries_downloader.cli.BatchDownloader"
        ) as mock_downloader_class:
            # Configure mocks
            mock_parser = Mock()
            mock_parser.parse_series_page.return_value = mock_series_info
            mock_parser_class.create_default.return_value = mock_parser

            mock_downloader = Mock()
            # Partial success
            mock_downloader.download_series.return_value = BatchDownloadResult(
                total_episodes=3, successful=2, failed=1, skipped=0, results=[], total_duration_seconds=5.0
            )
            mock_downloader_class.create_default.return_value = mock_downloader

            # Run CLI
            result = cli_runner.invoke(main, ["--url", "https://www.weekseries.info/series/test-series"])

            # Should exit with success code (at least one succeeded)
            assert result.exit_code == 0

    def test_backward_compatibility_episode_url(self, cli_runner):
        """Test that episode URLs still work (backward compatibility)"""
        with patch("weekseries_downloader.cli.URLExtractor") as mock_extractor_class, patch(
            "weekseries_downloader.cli.HLSDownloader"
        ) as mock_downloader_class:
            # Configure mocks for single episode download
            mock_extractor = Mock()
            from weekseries_downloader.models import ExtractionResult, EpisodeInfo

            mock_extractor.extract_stream_url.return_value = ExtractionResult(
                success=True,
                stream_url="https://example.com/stream.m3u8",
                referer_url="https://www.weekseries.info",
                episode_info=EpisodeInfo(series_name="test", season=1, episode=1, original_url="test"),
            )
            mock_extractor_class.create_default.return_value = mock_extractor

            mock_downloader = Mock()
            mock_downloader.download.return_value = True
            mock_downloader_class.create_default.return_value = mock_downloader

            # Run CLI with episode URL (not series URL)
            result = cli_runner.invoke(main, ["--url", "https://www.weekseries.info/series/test/temporada-1/episodio-01"])

            # Should use single-episode download path
            assert result.exit_code == 0
            mock_extractor.extract_stream_url.assert_called_once()
            mock_downloader.download.assert_called_once()

    def test_backward_compatibility_direct_stream_url(self, cli_runner):
        """Test that direct stream URLs still work"""
        with patch("weekseries_downloader.cli.HLSDownloader") as mock_downloader_class:
            # Configure mock
            mock_downloader = Mock()
            mock_downloader.download.return_value = True
            mock_downloader_class.create_default.return_value = mock_downloader

            # Run CLI with direct stream URL
            result = cli_runner.invoke(main, ["--url", "https://example.com/stream.m3u8"])

            # Should work without series parsing
            assert result.exit_code == 0
            mock_downloader.download.assert_called_once()

    def test_backward_compatibility_base64_url(self, cli_runner):
        """Test that base64 encoded URLs still work"""
        with patch("weekseries_downloader.cli.HLSDownloader") as mock_downloader_class:
            # Configure mock
            mock_downloader = Mock()
            mock_downloader.download.return_value = True
            mock_downloader_class.create_default.return_value = mock_downloader

            # Run CLI with base64 encoded URL
            base64_url = "aHR0cHM6Ly9leGFtcGxlLmNvbS9zdHJlYW0ubTN1OA=="  # https://example.com/stream.m3u8
            result = cli_runner.invoke(main, ["--encoded", base64_url])

            # Should work
            assert result.exit_code == 0
            mock_downloader.download.assert_called_once()

    def test_series_download_exception_handling(self, cli_runner):
        """Test that exceptions during series download are handled gracefully"""
        with patch("weekseries_downloader.cli.SeriesParser") as mock_parser_class:
            # Configure mock to raise exception
            mock_parser = Mock()
            mock_parser.parse_series_page.side_effect = Exception("Network error")
            mock_parser_class.create_default.return_value = mock_parser

            # Run CLI
            result = cli_runner.invoke(main, ["--url", "https://www.weekseries.info/series/test-series"])

            # Should exit with error code
            assert result.exit_code == 1
            assert "Network error" in result.output or result.exit_code == 1

    def test_cli_help_includes_series_options(self, cli_runner):
        """Test that help text includes new series download options"""
        result = cli_runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "--season" in result.output
        assert "--output-dir" in result.output
        assert "--continue-on-error" in result.output or "--stop-on-error" in result.output

    def test_multiple_options_combined(self, cli_runner, mock_series_info, mock_batch_result_success):
        """Test using multiple options together"""
        with patch("weekseries_downloader.cli.SeriesParser") as mock_parser_class, patch(
            "weekseries_downloader.cli.BatchDownloader"
        ) as mock_downloader_class:
            # Configure mocks
            mock_parser = Mock()
            mock_parser.parse_series_page.return_value = mock_series_info
            mock_parser_class.create_default.return_value = mock_parser

            mock_downloader = Mock()
            mock_downloader.download_series.return_value = mock_batch_result_success
            mock_downloader_class.create_default.return_value = mock_downloader

            # Run CLI with multiple options
            result = cli_runner.invoke(
                main,
                [
                    "--url",
                    "https://www.weekseries.info/series/test-series",
                    "--season",
                    "2",
                    "--output-dir",
                    "/my/videos",
                    "--no-convert",
                    "--stop-on-error",
                ],
            )

            # Verify all options were passed correctly
            assert result.exit_code == 0
            config = mock_downloader.download_series.call_args[0][0]
            assert config.season_filter == 2
            assert config.output_dir == "/my/videos"
            assert config.convert_to_mp4 is False
            assert config.continue_on_error is False
