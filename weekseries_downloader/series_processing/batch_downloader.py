"""
Batch downloader for downloading multiple episodes from a series
"""

import logging
import os
import time
from pathlib import Path
from typing import Optional

from ..models import (
    BatchDownloadConfig,
    BatchDownloadResult,
    EpisodeDownloadResult,
    EpisodeLink,
)
from ..url_processing.url_extractor import URLExtractor
from ..download.hls_downloader import HLSDownloader
from ..output.filename_generator import FilenameGenerator

logger = logging.getLogger(__name__)


class BatchDownloader:
    """Downloads multiple episodes from a series"""

    def __init__(
        self,
        url_extractor: Optional[URLExtractor] = None,
        hls_downloader: Optional[HLSDownloader] = None,
        filename_generator: Optional[FilenameGenerator] = None,
    ):
        """
        Initialize BatchDownloader with dependencies

        Args:
            url_extractor: URL extractor for getting stream URLs
            hls_downloader: HLS downloader for downloading episodes
            filename_generator: Filename generator for creating episode filenames
        """
        self.url_extractor = url_extractor or URLExtractor.create_default()
        self.hls_downloader = hls_downloader or HLSDownloader.create_default()
        self.filename_generator = filename_generator or FilenameGenerator()

    @classmethod
    def create_default(cls) -> "BatchDownloader":
        """Factory method with default dependencies"""
        return cls()

    def download_series(self, config: BatchDownloadConfig) -> BatchDownloadResult:
        """
        Download multiple episodes from series

        Steps:
        1. Filter episodes by season if specified
        2. Create output directory if needed
        3. For each episode:
           a. Check if already exists (skip)
           b. Extract stream URL from episode page
           c. Generate output filename
           d. Download using HLSDownloader
           e. Track result (success/failure)
        4. Return batch results with statistics

        Args:
            config: Batch download configuration

        Returns:
            BatchDownloadResult with statistics and per-episode results
        """
        logger.info(f"Starting batch download for {config.series_info.series_name}")

        start_time = time.time()

        # Filter episodes by season
        episodes = config.series_info.get_episodes(config.season_filter)

        if not episodes:
            logger.warning("No episodes to download after filtering")
            return BatchDownloadResult(total_episodes=0, successful=0, failed=0, skipped=0, results=[], total_duration_seconds=0.0)

        # Create output directory
        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {output_dir}")

        # Download each episode
        results = []
        successful = 0
        failed = 0
        skipped = 0

        for i, episode_link in enumerate(episodes, 1):
            logger.info(f"Processing episode {i}/{len(episodes)}: {episode_link}")

            result = self._download_single_episode(episode_link, config)
            results.append(result)

            if result.success:
                successful += 1
                logger.info(f"✓ Downloaded: {result.output_path}")
            elif result.output_path:  # File already exists
                skipped += 1
                logger.info(f"↷ Skipped (already exists): {result.output_path}")
            else:
                failed += 1
                logger.error(f"✗ Failed: {result.error_message}")

                # Stop on error if configured
                if not config.continue_on_error:
                    logger.warning("Stopping due to error (continue_on_error=False)")
                    break

        total_duration = time.time() - start_time

        batch_result = BatchDownloadResult(
            total_episodes=len(episodes),
            successful=successful,
            failed=failed,
            skipped=skipped,
            results=results,
            total_duration_seconds=total_duration,
        )

        logger.info(f"Batch download complete: {batch_result}")
        return batch_result

    def _download_single_episode(self, episode_link: EpisodeLink, config: BatchDownloadConfig) -> EpisodeDownloadResult:
        """
        Download a single episode and return result

        Args:
            episode_link: Episode to download
            config: Batch download configuration

        Returns:
            EpisodeDownloadResult with success status and details
        """
        start_time = time.time()

        # Generate output filename
        extension = "mp4" if config.convert_to_mp4 else "ts"
        filename = self.filename_generator.generate_series_episode_filename(
            config.series_info.series_name, episode_link.season, episode_link.episode, extension
        )

        output_path = os.path.join(config.output_dir, filename)

        # Check if file already exists
        if self._check_existing_file(output_path):
            logger.debug(f"File already exists: {output_path}")
            duration = time.time() - start_time
            return EpisodeDownloadResult(
                episode_link=episode_link, success=False, output_path=output_path, error_message=None, duration_seconds=duration
            )

        # Extract stream URL from episode page
        try:
            logger.debug(f"Extracting stream URL from: {episode_link.full_url}")
            extraction_result = self.url_extractor.extract_stream_url(episode_link.full_url)

            if not extraction_result.success:
                duration = time.time() - start_time
                return EpisodeDownloadResult(
                    episode_link=episode_link,
                    success=False,
                    error_message=f"Failed to extract stream URL: {extraction_result.error_message}",
                    duration_seconds=duration,
                )

            stream_url = extraction_result.stream_url
            referer = extraction_result.referer_url

            # Additional safety check for type checker
            if not stream_url:
                duration = time.time() - start_time
                return EpisodeDownloadResult(
                    episode_link=episode_link,
                    success=False,
                    error_message="Stream URL is empty after extraction",
                    duration_seconds=duration,
                )

        except Exception as e:
            duration = time.time() - start_time
            logger.exception(f"Exception during stream URL extraction: {e}")
            return EpisodeDownloadResult(
                episode_link=episode_link, success=False, error_message=f"Extraction error: {str(e)}", duration_seconds=duration
            )

        # Download episode
        try:
            logger.debug(f"Downloading to: {output_path}")
            success = self.hls_downloader.download(
                stream_url=stream_url, output_path=Path(output_path), referer=referer, convert_to_mp4=config.convert_to_mp4
            )

            duration = time.time() - start_time

            if success:
                return EpisodeDownloadResult(episode_link=episode_link, success=True, output_path=output_path, duration_seconds=duration)
            else:
                return EpisodeDownloadResult(episode_link=episode_link, success=False, error_message="Download failed", duration_seconds=duration)

        except Exception as e:
            duration = time.time() - start_time
            logger.exception(f"Exception during download: {e}")
            return EpisodeDownloadResult(
                episode_link=episode_link, success=False, error_message=f"Download error: {str(e)}", duration_seconds=duration
            )

    def _check_existing_file(self, output_path: str) -> bool:
        """
        Check if episode file already exists

        Args:
            output_path: Path to check

        Returns:
            True if file exists and has non-zero size
        """
        if not os.path.exists(output_path):
            return False

        # Check if file has content
        file_size = os.path.getsize(output_path)
        if file_size == 0:
            logger.warning(f"Found empty file, will re-download: {output_path}")
            return False

        return True
