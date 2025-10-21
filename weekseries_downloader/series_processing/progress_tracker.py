"""
Progress tracking for batch downloads
"""

import logging
import time
from typing import Optional

from ..models import EpisodeLink, EpisodeDownloadResult, BatchDownloadResult

logger = logging.getLogger(__name__)


class ProgressTracker:
    """Tracks progress for batch downloads with console output"""

    def __init__(self, total_episodes: int):
        """
        Initialize progress tracker

        Args:
            total_episodes: Total number of episodes to download
        """
        self.total_episodes = total_episodes
        self.current_episode = 0
        self.successful = 0
        self.failed = 0
        self.skipped = 0
        self.start_time: Optional[float] = None
        self.results = []

    def start_batch(self):
        """Initialize batch download tracking"""
        self.start_time = time.time()
        logger.info(f"Starting batch download of {self.total_episodes} episodes")

    def start_episode(self, episode_link: EpisodeLink):
        """
        Mark episode download start

        Args:
            episode_link: Episode being downloaded
        """
        self.current_episode += 1
        logger.info(f"[{self.current_episode}/{self.total_episodes}] Starting {episode_link}")

    def complete_episode(self, result: EpisodeDownloadResult):
        """
        Mark episode download completion

        Args:
            result: Result of episode download
        """
        self.results.append(result)

        if result.success:
            self.successful += 1
            logger.info(f"✓ Success: {result.output_path} ({result.duration_seconds:.1f}s)")
        elif result.output_path:  # File already exists (skipped)
            self.skipped += 1
            logger.info(f"↷ Skipped: {result.output_path} (already exists)")
        else:
            self.failed += 1
            logger.error(f"✗ Failed: {result.error_message}")

    def finish_batch(self) -> BatchDownloadResult:
        """
        Finalize batch and return results

        Returns:
            BatchDownloadResult with statistics
        """
        total_duration = time.time() - self.start_time if self.start_time else 0.0

        result = BatchDownloadResult(
            total_episodes=self.total_episodes,
            successful=self.successful,
            failed=self.failed,
            skipped=self.skipped,
            results=self.results,
            total_duration_seconds=total_duration,
        )

        self.print_summary(result)
        return result

    def print_summary(self, result: BatchDownloadResult):
        """
        Print final summary of batch download

        Args:
            result: Batch download result
        """
        logger.info("=" * 60)
        logger.info("BATCH DOWNLOAD SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total episodes: {result.total_episodes}")
        logger.info(f"✓ Successful:   {result.successful}")
        logger.info(f"↷ Skipped:      {result.skipped}")
        logger.info(f"✗ Failed:       {result.failed}")
        logger.info(f"Duration:       {result.total_duration_seconds:.1f}s")

        if result.successful > 0:
            avg_time = sum(r.duration_seconds for r in result.results if r.success) / result.successful
            logger.info(f"Avg time/ep:    {avg_time:.1f}s")

        logger.info("=" * 60)
