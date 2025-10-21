"""
Tests for HLSDownloader class
"""

from unittest.mock import Mock
from weekseries_downloader.download.hls_downloader import HLSDownloader


class TestHLSDownloaderFileSkip:
    """Test file existence validation and skip behavior"""

    def test_skip_existing_mp4_file(self, tmp_path):
        """Test that existing .mp4 file is skipped"""
        # Create existing output file
        output_file = tmp_path / "test_video.mp4"
        output_file.write_text("existing video content")

        # Create downloader with mocked dependencies
        downloader = HLSDownloader()

        # Mock all the download methods (should not be called)
        downloader.http_client = Mock()
        downloader.playlist_parser = Mock()
        downloader.segment_downloader = Mock()

        # Attempt download
        result = downloader.download(
            stream_url="https://example.com/stream.m3u8",
            output_path=output_file,
            convert_to_mp4=True,
        )

        # Should return True without downloading
        assert result is True

        # Verify no network calls were made
        downloader.http_client.fetch.assert_not_called()
        downloader.playlist_parser.parse_segments.assert_not_called()
        downloader.segment_downloader.download_segments_parallel.assert_not_called()

    def test_skip_existing_ts_file_no_convert_mode(self, tmp_path):
        """Test that existing .ts file is skipped in no-convert mode"""
        # Create existing output file
        output_file = tmp_path / "test_video.ts"
        output_file.write_text("existing video content")

        # Create downloader
        downloader = HLSDownloader()

        # Mock dependencies
        downloader.http_client = Mock()
        downloader.playlist_parser = Mock()
        downloader.segment_downloader = Mock()

        # Attempt download with no conversion
        result = downloader.download(
            stream_url="https://example.com/stream.m3u8",
            output_path=output_file,
            convert_to_mp4=False,
        )

        # Should return True without downloading
        assert result is True

        # Verify no download occurred
        downloader.http_client.fetch.assert_not_called()

    def test_skip_empty_file_should_redownload(self, tmp_path):
        """Test that empty files are NOT skipped (re-download)"""
        # Create empty output file
        output_file = tmp_path / "test_video.mp4"
        output_file.touch()  # Empty file

        # Create downloader
        downloader = HLSDownloader()

        # Mock dependencies to simulate successful download
        downloader.http_client = Mock()
        downloader.http_client.get_weekseries_headers.return_value = {}
        downloader.http_client.fetch.return_value = "#EXTM3U\nsegment1.ts\n"

        downloader.playlist_parser = Mock()
        downloader.playlist_parser.is_master_playlist.return_value = False
        downloader.playlist_parser.get_base_url.return_value = "https://example.com/"
        downloader.playlist_parser.parse_segments.return_value = ["segment1.ts"]

        downloader.segment_downloader = Mock()
        downloader.segment_downloader.download_segments_parallel.return_value = True

        downloader.media_converter = Mock()
        downloader.media_converter.is_ffmpeg_available.return_value = False

        # Attempt download
        result = downloader.download(
            stream_url="https://example.com/stream.m3u8",
            output_path=output_file,
            convert_to_mp4=True,
        )

        # Should proceed with download (not skip)
        assert result is True
        downloader.http_client.fetch.assert_called()

    def test_proceed_with_download_if_file_does_not_exist(self, tmp_path):
        """Test that download proceeds when output file doesn't exist"""
        # Output file does not exist
        output_file = tmp_path / "test_video.mp4"

        # Create downloader
        downloader = HLSDownloader()

        # Mock successful download workflow
        downloader.http_client = Mock()
        downloader.http_client.get_weekseries_headers.return_value = {}
        downloader.http_client.fetch.return_value = "#EXTM3U\nsegment1.ts\n"

        downloader.playlist_parser = Mock()
        downloader.playlist_parser.is_master_playlist.return_value = False
        downloader.playlist_parser.get_base_url.return_value = "https://example.com/"
        downloader.playlist_parser.parse_segments.return_value = ["segment1.ts"]

        downloader.segment_downloader = Mock()
        downloader.segment_downloader.download_segments_parallel.return_value = True

        downloader.media_converter = Mock()
        downloader.media_converter.is_ffmpeg_available.return_value = False

        # Attempt download
        result = downloader.download(
            stream_url="https://example.com/stream.m3u8",
            output_path=output_file,
            convert_to_mp4=True,
        )

        # Should proceed with download
        assert result is True
        downloader.http_client.fetch.assert_called()
        downloader.segment_downloader.download_segments_parallel.assert_called()

    def test_skip_existing_file_with_convert_flag_mp4_exists(self, tmp_path):
        """Test skip behavior when .mp4 exists even with convert_to_mp4=True"""
        # Create existing .mp4 file
        output_file = tmp_path / "test_video.mp4"
        output_file.write_text("existing mp4 content")

        # Create downloader
        downloader = HLSDownloader()

        # Mock dependencies (should not be called)
        downloader.http_client = Mock()
        downloader.media_converter = Mock()

        # Attempt download with conversion enabled
        result = downloader.download(
            stream_url="https://example.com/stream.m3u8",
            output_path=output_file,
            convert_to_mp4=True,
        )

        # Should skip
        assert result is True
        downloader.http_client.fetch.assert_not_called()
        downloader.media_converter.convert_to_mp4.assert_not_called()

    def test_download_proceeds_when_ts_exists_but_mp4_requested(self, tmp_path):
        """Test that download proceeds when .ts exists but .mp4 is requested"""
        # Create existing .ts file (from partial download)
        ts_file = tmp_path / "test_video.ts"
        ts_file.write_text("partial ts content")

        # But .mp4 is requested and doesn't exist
        output_file = tmp_path / "test_video.mp4"

        # Create downloader
        downloader = HLSDownloader()

        # Mock successful download
        downloader.http_client = Mock()
        downloader.http_client.get_weekseries_headers.return_value = {}
        downloader.http_client.fetch.return_value = "#EXTM3U\nsegment1.ts\n"

        downloader.playlist_parser = Mock()
        downloader.playlist_parser.is_master_playlist.return_value = False
        downloader.playlist_parser.get_base_url.return_value = "https://example.com/"
        downloader.playlist_parser.parse_segments.return_value = ["segment1.ts"]

        downloader.segment_downloader = Mock()
        downloader.segment_downloader.download_segments_parallel.return_value = True

        downloader.media_converter = Mock()
        downloader.media_converter.is_ffmpeg_available.return_value = True
        downloader.media_converter.convert_to_mp4.return_value = True

        # Attempt download
        result = downloader.download(
            stream_url="https://example.com/stream.m3u8",
            output_path=output_file,
            convert_to_mp4=True,
        )

        # Should proceed with download (resume from .ts if needed)
        assert result is True
        downloader.segment_downloader.download_segments_parallel.assert_called()
