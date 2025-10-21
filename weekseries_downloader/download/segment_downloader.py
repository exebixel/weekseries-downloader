"""
HLS segment downloader
"""

from pathlib import Path
from typing import List, Optional
import urllib.request
import urllib.error
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
from alive_progress import alive_bar
from ..output.file_manager import FileManager
from .segment_buffer import SegmentBuffer, BufferedSegment


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

    def download_segments_parallel(
        self,
        segment_urls: List[str],
        output_file: Path,
        file_manager: FileManager,
        referer: Optional[str] = None,
        max_workers: int = 8,
        buffer_size: int = 50,
    ) -> bool:
        """
        Download segments in parallel with ordered writing and resume support

        Architecture:
            - Download Pool: N worker threads downloading segments concurrently
            - Segment Buffer: Thread-safe in-memory buffer (max 50 segments)
            - Writer Thread: Single thread writing segments in order to disk
            - Resume: Calculates position from existing .ts file size

        Args:
            segment_urls: All segment URLs
            output_file: Output .ts file path
            file_manager: File manager for append operations
            referer: Referer header
            max_workers: Number of parallel download threads (default 8)
            buffer_size: Max segments to buffer in memory (default 50)

        Returns:
            True if all segments downloaded successfully
        """
        total_segments = len(segment_urls)

        # Calculate resume position from existing file
        completed_count = 0
        if output_file.exists():
            self.logger.info("Found existing partial download, calculating resume position...")
            # Download first segment to estimate average size
            first_seg_data = self.download_single_segment(segment_urls[0], referer)
            if first_seg_data:
                avg_size = len(first_seg_data)
                current_size = file_manager.get_file_size(output_file)
                completed_count = min(current_size // avg_size, total_segments)
                self.logger.info(
                    f"Resuming from segment {completed_count}/{total_segments} " f"(file size: {current_size} bytes, avg segment: {avg_size} bytes)"
                )

        remaining_segments = total_segments - completed_count
        next_write_index = completed_count + 1

        if remaining_segments == 0:
            self.logger.info("All segments already downloaded!")
            return True

        buffer = SegmentBuffer(max_buffer_size=buffer_size)
        download_errors = []
        stop_event = threading.Event()

        # Progress bar reference (will be set by alive_bar context)
        progress_bar = None
        bar_lock = threading.Lock()

        # Writer thread - writes segments in order to disk
        def writer_worker():
            nonlocal next_write_index

            while next_write_index <= total_segments:
                # Wait for next segment in sequence
                segment = buffer.get_next_segment(next_write_index)

                if segment is None:
                    if stop_event.is_set():
                        break
                    time.sleep(0.1)  # Wait for segment to be downloaded
                    continue

                # Append to output file
                success = file_manager.append_segment_to_file(segment.data, output_file)

                if not success:
                    self.logger.error(f"Failed to write segment {segment.index}")
                    stop_event.set()
                    return False

                # Update progress bar
                with bar_lock:
                    if progress_bar is not None:
                        progress_bar()
                        mem_usage_mb = buffer.get_memory_usage() / (1024 * 1024)
                        progress_bar.text(f"Buffer: {buffer.size()} segments ({mem_usage_mb:.1f}MB)")

                next_write_index += 1

            return True

        # Start writer thread
        writer_thread = threading.Thread(target=writer_worker, daemon=True)
        writer_thread.start()

        # Download segments in parallel with progress bar
        with alive_bar(remaining_segments, title="Downloading segments") as bar:
            # Store bar reference for writer thread
            with bar_lock:
                progress_bar = bar

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit download tasks for remaining segments
                future_to_index = {}

                for i in range(completed_count + 1, total_segments + 1):
                    url = segment_urls[i - 1]  # URLs are 0-indexed
                    future = executor.submit(self._download_with_index, i, url, referer)
                    future_to_index[future] = i

                # Process completed downloads
                for future in as_completed(future_to_index):
                    index = future_to_index[future]

                    try:
                        segment_data = future.result()

                        if segment_data is None:
                            download_errors.append(index)
                            self.logger.warning(f"Failed to download segment {index}")
                            continue

                        # Add to buffer (wait if buffer is full)
                        buffered_segment = BufferedSegment(index=index, data=segment_data, size=len(segment_data))

                        while not buffer.add_segment(buffered_segment):
                            if stop_event.is_set():
                                break
                            time.sleep(0.1)  # Wait for buffer space

                    except Exception as e:
                        self.logger.error(f"Error processing segment {index}: {e}")
                        download_errors.append(index)

        # Signal writer to finish
        stop_event.set()
        writer_thread.join(timeout=30)

        # Check for errors
        if download_errors:
            self.logger.error(f"Failed to download {len(download_errors)} segments")
            return False

        self.logger.info("All segments downloaded and written!")
        return True

    def _download_with_index(self, index: int, url: str, referer: Optional[str]) -> Optional[bytes]:
        """
        Download single segment with index (for parallel execution)

        Args:
            index: Segment index (1-based) - used by caller for tracking
            url: Segment URL
            referer: Referer header

        Returns:
            Segment data or None if failed
        """
        _ = index  # Parameter used by caller for tracking, not needed in method body
        return self.download_single_segment(url, referer)
