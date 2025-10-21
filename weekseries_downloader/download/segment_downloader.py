"""
HLS segment downloader
"""

from pathlib import Path
from typing import List, Optional
import urllib.request
import urllib.error
import logging
from ..output.file_manager import FileManager


class SegmentDownloader:
    """Download individual HLS segments"""

    def __init__(self, file_manager: Optional[FileManager] = None, timeout: int = 30):
        """
        Initialize segment downloader

        Args:
            file_manager: File manager for saving segments
            timeout: Request timeout in seconds
        """
        self.file_manager = file_manager or FileManager()
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)

    def download_segments(self, segment_urls: List[str], output_dir: Path, referer: Optional[str] = None) -> tuple[bool, List[Path]]:
        """
        Download all segments to output directory

        Args:
            segment_urls: List of segment URLs
            output_dir: Directory to save segments
            referer: Referer URL for requests

        Returns:
            Tuple of (success: bool, downloaded_files: List[Path])
        """
        total_segments = len(segment_urls)
        self.logger.info(f"Total segments: {total_segments}")
        self.logger.info("Downloading segments... (this may take a few minutes)")

        downloaded_files = []

        try:
            for i, segment_url in enumerate(segment_urls, 1):
                # Show progress
                percent = (i / total_segments) * 100

                # Log progress every 10% or on last segment
                if i % max(1, total_segments // 10) == 0 or i == total_segments:
                    self.logger.info(f"Progress: {i}/{total_segments} ({percent:.1f}%)")

                # Download segment
                segment_data = self.download_single_segment(segment_url, referer)

                if segment_data is None:
                    self.logger.warning(f"Failed to download segment {i}, continuing...")
                    continue

                # Save segment
                segment_file = self.file_manager.save_segment(segment_data, output_dir, i)

                if segment_file:
                    downloaded_files.append(segment_file)

            if len(downloaded_files) == 0:
                self.logger.error("No segments downloaded successfully")
                return False, []

            self.logger.info("All segments downloaded!")
            return True, downloaded_files

        except KeyboardInterrupt:
            self.logger.info("Download cancelled by user")
            return False, downloaded_files

        except Exception as e:
            self.logger.error(f"Error downloading segments: {e}")
            return False, downloaded_files

    def download_single_segment(self, segment_url: str, referer: Optional[str] = None) -> Optional[bytes]:
        """
        Download single segment file

        Args:
            segment_url: Segment URL
            referer: Referer URL for request

        Returns:
            Segment binary data or None if failed
        """
        try:
            req = self._create_segment_request(segment_url, referer)

            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return response.read()

        except urllib.error.HTTPError as e:
            self.logger.error(f"HTTP error downloading segment {segment_url}: {e.code} {e.reason}")
            return None

        except urllib.error.URLError as e:
            self.logger.error(f"URL error downloading segment {segment_url}: {e.reason}")
            return None

        except Exception as e:
            self.logger.error(f"Error downloading segment {segment_url}: {e}")
            return None

    def _create_segment_request(self, url: str, referer: Optional[str] = None) -> urllib.request.Request:
        """
        Create HTTP request for segment download

        Args:
            url: Segment URL
            referer: Referer URL

        Returns:
            Configured Request object
        """
        req = urllib.request.Request(url)

        # Add headers
        req.add_header(
            "User-Agent",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) " "AppleWebKit/537.36 (KHTML, like Gecko) " "Chrome/131.0.0.0 Safari/537.36",
        )

        if referer:
            req.add_header("Referer", referer)
        else:
            req.add_header("Referer", "https://www.weekseries.info/")

        req.add_header("Origin", "https://www.weekseries.info")
        req.add_header("Accept", "*/*")

        return req
