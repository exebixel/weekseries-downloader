"""
Main HLS video download orchestrator
"""

from pathlib import Path
from typing import Optional
import logging
from .playlist_parser import PlaylistParser
from .segment_downloader import SegmentDownloader
from .media_converter import MediaConverter
from ..infrastructure.http_client import HTTPClient
from ..output.file_manager import FileManager


class HLSDownloader:
    """Main HLS video download orchestrator"""

    def __init__(
        self,
        http_client: Optional[HTTPClient] = None,
        playlist_parser: Optional[PlaylistParser] = None,
        segment_downloader: Optional[SegmentDownloader] = None,
        file_manager: Optional[FileManager] = None,
        media_converter: Optional[MediaConverter] = None,
    ):
        """
        Initialize with dependency injection

        Args:
            http_client: HTTP client for requests
            playlist_parser: Parser for m3u8 playlists
            segment_downloader: Downloader for segments
            file_manager: Manager for file operations
            media_converter: Converter for video formats
        """
        self.http_client = http_client or HTTPClient()
        self.playlist_parser = playlist_parser or PlaylistParser()
        self.segment_downloader = segment_downloader or SegmentDownloader()
        self.file_manager = file_manager or FileManager()
        self.media_converter = media_converter or MediaConverter()
        self.logger = logging.getLogger(__name__)

    def download(self, stream_url: str, output_path: Path, referer: Optional[str] = None, convert_to_mp4: bool = True) -> bool:
        """
        Download HLS video from stream URL

        Steps:
        1. Download m3u8 playlist
        2. Check if master playlist (multiple qualities)
        3. Select first quality if master
        4. Parse segment URLs
        5. Create temp directory
        6. Download all segments
        7. Concatenate segments
        8. Convert to mp4 (optional)
        9. Cleanup temp files

        Args:
            stream_url: HLS stream URL (m3u8)
            output_path: Output file path
            referer: Referer URL for requests
            convert_to_mp4: Whether to convert to MP4

        Returns:
            True if successful
        """
        self.logger.info(f"Stream URL: {stream_url}")
        self.logger.info(f"Saving to: {output_path}")
        self.logger.info("Downloading m3u8 playlist...")

        # 1. Download playlist
        headers = self.http_client.get_weekseries_headers(referer)
        playlist_content = self.http_client.fetch(stream_url, headers)

        if not playlist_content:
            self.logger.error("Could not download playlist")
            return False

        # 2-3. Handle master playlist
        if self.playlist_parser.is_master_playlist(playlist_content):
            self.logger.info("Master playlist detected with multiple qualities")
            self.logger.info("Selecting best quality...")

            base_url = self.playlist_parser.get_base_url(stream_url)
            quality_url = self.playlist_parser.get_first_quality_url(playlist_content, base_url)

            if quality_url:
                self.logger.info(f"Downloading quality playlist: {quality_url}")
                playlist_content = self.http_client.fetch(quality_url, headers)
                stream_url = quality_url  # Update base URL

                if not playlist_content:
                    self.logger.error("Could not download sub-playlist")
                    return False

        # 4. Parse segments
        base_url = self.playlist_parser.get_base_url(stream_url)
        segments = self.playlist_parser.parse_segments(playlist_content, base_url)

        if not segments:
            self.logger.error("No segments found in playlist")
            return False

        # 5-6. Create temp dir and download segments
        temp_dir = self.file_manager.create_temp_dir(output_path)

        success, downloaded_files = self.segment_downloader.download_segments(segments, temp_dir, referer)

        if not success or not downloaded_files:
            self.logger.error("Failed to download segments")
            self.file_manager.cleanup(temp_dir)
            return False

        # 7. Concatenate segments
        ts_file = output_path if not convert_to_mp4 else output_path.with_suffix(".ts")

        if not self.file_manager.concatenate_segments(temp_dir, ts_file):
            self.logger.error("Failed to concatenate segments")
            self.file_manager.cleanup_segments(downloaded_files, temp_dir)
            return False

        self.logger.info(f"Complete TS file: {ts_file}")

        # Clean up segment files
        self.file_manager.cleanup_segments(downloaded_files, temp_dir)

        # 8. Convert to MP4
        if convert_to_mp4 and output_path.suffix == ".mp4":
            if not self.media_converter.is_ffmpeg_available():
                self.logger.warning("ffmpeg not found, keeping .ts file")
                self.logger.info("Install ffmpeg with: brew install ffmpeg")
                self.logger.info(f"Or convert manually: ffmpeg -i {ts_file} -c copy {output_path}")
                return True

            if self.media_converter.convert_to_mp4(ts_file, output_path):
                # Remove .ts file after successful conversion
                self.logger.info("Removing temporary .ts file...")
                try:
                    ts_file.unlink()
                    self.logger.info(f"Final file: {output_path}")
                except Exception as e:
                    self.logger.warning(f"Could not remove {ts_file}: {e}")
            else:
                self.logger.warning(f"Conversion failed, .ts file kept: {ts_file}")

        return True

    @classmethod
    def create_default(cls) -> "HLSDownloader":
        """
        Factory method with default dependencies

        Returns:
            HLSDownloader with default configuration
        """
        return cls(
            http_client=HTTPClient(),
            playlist_parser=PlaylistParser(),
            segment_downloader=SegmentDownloader(),
            file_manager=FileManager(),
            media_converter=MediaConverter(),
        )
