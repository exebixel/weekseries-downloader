"""
Command line interface for WeekSeries Downloader
"""

import sys
import logging
import click
from pathlib import Path
from typing import Optional, Tuple

from weekseries_downloader.models import EpisodeInfo, BatchDownloadConfig
from weekseries_downloader.url_processing import URLParser, URLType, URLExtractor
from weekseries_downloader.download import HLSDownloader
from weekseries_downloader.output import FilenameGenerator
from weekseries_downloader.infrastructure import LoggingConfig, Base64Parser
from weekseries_downloader.series_processing import SeriesParser, BatchDownloader

logger = logging.getLogger(__name__)


def process_url_input(url: Optional[str], encoded: Optional[str]) -> Tuple[Optional[str], Optional[str], Optional[str], Optional["EpisodeInfo"]]:
    """
    Process URL input using early returns

    Args:
        url: URL provided by user
        encoded: Base64 encoded URL

    Returns:
        Tuple (stream_url, error_message, referer_url, episode_info)
    """

    # Early return for encoded URL
    if encoded:
        logger.info("Decoding base64 URL...")
        decoded = Base64Parser.decode(encoded)
        if not decoded:
            return None, "Failed to decode base64 URL", None, None
        return decoded, None, None, None

    # Early return if no URL provided
    if not url:
        return None, "You must provide --url or --encoded", None, None

    url_type = URLParser.detect_url_type(url)

    # Early return for direct streaming URL
    if url_type == URLType.DIRECT_STREAM:
        return url, None, None, None

    # Early return for weekseries URL
    if url_type == URLType.WEEKSERIES:
        logger.info("Extracting streaming URL from weekseries page...")

        extractor = URLExtractor.create_default()
        result = extractor.extract_stream_url(url)

        if not result.success:
            return None, result.error_message, None, None

        logger.info("Streaming URL extracted successfully")

        # Return episode info for filename generation
        if result.episode_info:
            logger.info(f"Detected episode: {result.episode_info}")

        return result.stream_url, None, result.referer_url, result.episode_info

    # Early return for direct base64
    if url_type == URLType.BASE64:
        logger.info("Decoding base64 URL...")
        decoded = Base64Parser.decode(url)
        if not decoded:
            return None, "Failed to decode base64 URL", None, None
        return decoded, None, None, None

    return None, "URL type not supported. Use weekseries.info URLs or direct streaming URLs.", None, None


def _handle_series_download(
    series_url: str, output_dir: Optional[str], season_filter: Optional[int], no_convert: bool, continue_on_error: bool
) -> int:
    """
    Handle downloading an entire series

    Args:
        series_url: URL of the series page
        output_dir: Output directory (None for default)
        season_filter: Season number to filter (None for all)
        no_convert: If True, keep .ts files; if False, convert to MP4
        continue_on_error: If True, continue on per-episode errors

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Parse series page to get episodes
        logger.info("Parsing series page...")
        parser = SeriesParser.create_default()
        series_info = parser.parse_series_page(series_url)

        logger.info(f"Found {series_info}")

        # Determine output directory
        if output_dir is None:
            output_dir = f"./{series_info.series_name}"

        # Create batch download configuration
        config = BatchDownloadConfig(
            series_info=series_info,
            season_filter=season_filter,
            output_dir=output_dir,
            convert_to_mp4=not no_convert,
            continue_on_error=continue_on_error,
        )

        # Download episodes
        logger.info(f"Starting batch download to {output_dir}")
        batch_downloader = BatchDownloader.create_default()
        result = batch_downloader.download_series(config)

        # Print summary
        logger.info("=" * 60)
        logger.info("BATCH DOWNLOAD COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total episodes: {result.total_episodes}")
        logger.info(f"✓ Successful:   {result.successful}")
        logger.info(f"↷ Skipped:      {result.skipped}")
        logger.info(f"✗ Failed:       {result.failed}")
        logger.info(f"Duration:       {result.total_duration_seconds:.1f}s")
        logger.info("=" * 60)

        # Exit with appropriate code
        if result.failed > 0 and result.successful == 0:
            logger.error("All downloads failed")
            return 1

        if result.successful > 0:
            logger.info(f"Downloaded {result.successful} episodes to {output_dir}")
            return 0

        logger.warning("No episodes were downloaded")
        return 1

    except Exception as e:
        logger.exception(f"Series download failed: {e}")
        return 1


@click.command()
@click.option("--url", "-u", help="weekseries.info URL (series or episode) or direct m3u8 stream")
@click.option("--encoded", "-e", help="Base64 encoded stream URL")
@click.option(
    "--output",
    "-o",
    default="video.mp4",
    help="Output filename for single episodes (default: automatically generated based on URL)",
)
@click.option(
    "--output-dir",
    "-d",
    type=click.Path(),
    help="Output directory for series downloads (default: ./series_name/)",
)
@click.option(
    "--season",
    "-s",
    type=int,
    help="Download specific season only (use with series URLs)",
)
@click.option(
    "--referer",
    "-r",
    help="Referer page URL (default: https://www.weekseries.info/)",
)
@click.option("--no-convert", is_flag=True, help="Do not convert to MP4, keep .ts only")
@click.option(
    "--continue-on-error/--stop-on-error",
    default=True,
    help="Continue downloading remaining episodes if one fails (default: continue)",
)
@click.version_option(version="0.1.0", prog_name="weekseries-dl")
def main(url, encoded, output, output_dir, season, referer, no_convert, continue_on_error):
    """
    WeekSeries Downloader - Download videos from WeekSeries using pure Python

    Examples:

    \b
    # Download single episode with automatic name:
    weekseries-dl --url "https://www.weekseries.info/series/the-good-doctor/temporada-1/episodio-01"
    # Result: the_good_doctor_S01E01.mp4

    \b
    # Download entire series:
    weekseries-dl --url "https://www.weekseries.info/series/the-good-doctor"
    # Result: ./the-good-doctor/the_good_doctor_S01E01.mp4, S01E02.mp4, ...

    \b
    # Download specific season:
    weekseries-dl --url "https://www.weekseries.info/series/the-good-doctor" --season 2
    # Result: ./the-good-doctor/the_good_doctor_S02E01.mp4, S02E02.mp4, ...

    \b
    # Custom output directory for series:
    weekseries-dl --url "https://www.weekseries.info/series/..." --output-dir ~/Videos/series/

    \b
    # Download using base64 encoded URL:
    weekseries-dl --encoded "aHR0cHM6Ly9zZXJpZXMudmlkbWFuaWl4LnNob3AvVC90aGUtZ29vZC1kb2N0b3IvMDItdGVtcG9yYWRhLzE2L3N0cmVhbS5tM3U4"

    \b
    # Download using direct streaming URL:
    weekseries-dl --url "https://series.vidmaniix.shop/T/the-good-doctor/02-temporada/16/stream.m3u8"
    # Result: the_good_doctor_02_temporada_16.mp4

    \b
    # With custom filename (single episode):
    weekseries-dl --url "https://www.weekseries.info/series/.../episodio-01" --output "my_episode.mp4"

    \b
    # Keep only .ts file (no conversion):
    weekseries-dl --url "..." --no-convert
    # Result: automatic_name.ts
    """

    # Setup logging
    LoggingConfig.setup_default()

    # Check if this is a series download
    if url and not encoded:
        url_type = URLParser.detect_url_type(url)

        if url_type == URLType.SERIES:
            # Handle series download
            logger.info(f"Detected series URL: {url}")
            exit_code = _handle_series_download(url, output_dir, season, no_convert, continue_on_error)
            sys.exit(exit_code)

    # Handle single episode download
    # Process URL using functional pattern
    stream_url, error, auto_referer, episode_info = process_url_input(url, encoded)

    if error:
        logger.error(f"URL processing error: {error}")
        logger.info("Supported formats: weekseries.info URLs (series or episode), direct streaming URLs, or base64 encoded URLs")
        sys.exit(1)

    # Generate filename automatically if needed
    generator = FilenameGenerator()
    output_filename = generator.generate(
        stream_url=stream_url,
        episode_info=episode_info,
        user_output=output if output != "video.mp4" else None,
        default_extension=".ts" if no_convert else ".mp4",
    )

    # Validate filename
    output_filename = FilenameGenerator.validate_filename(output_filename)
    output_path = Path(output_filename)

    # Set referer automatically if not provided
    final_referer = referer or auto_referer

    # Download the video
    downloader = HLSDownloader.create_default()
    convert_mp4 = not no_convert
    success = downloader.download(stream_url=stream_url, output_path=output_path, referer=final_referer, convert_to_mp4=convert_mp4)

    if success:
        logger.info(f"Download completed successfully: {output_path}")
    else:
        logger.error(f"Download failed for: {stream_url}")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
