"""
Command line interface for WeekSeries Downloader
"""

import sys
import click
from pathlib import Path
from typing import Optional, Tuple

from weekseries_downloader.models import EpisodeInfo
from weekseries_downloader.url_processing import URLParser, URLType, URLExtractor
from weekseries_downloader.download import HLSDownloader
from weekseries_downloader.output import FilenameGenerator
from weekseries_downloader.infrastructure import LoggingConfig, Base64Parser


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
        click.echo("Decoding URL...")
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
        click.echo("Extracting streaming URL...")

        extractor = URLExtractor.create_default()
        result = extractor.extract_stream_url(url)

        if not result.success:
            return None, result.error_message, None, None

        click.echo("Streaming URL extracted successfully")

        # Return episode info for filename generation
        if result.episode_info:
            click.echo(f"Detected: {result.episode_info}")

        return result.stream_url, None, result.referer_url, result.episode_info

    # Early return for direct base64
    if url_type == URLType.BASE64:
        click.echo("Decoding base64 URL...")
        decoded = Base64Parser.decode(url)
        if not decoded:
            return None, "Failed to decode base64 URL", None, None
        return decoded, None, None, None

    return None, "URL type not supported. Use weekseries.info URLs or direct streaming URLs.", None, None


@click.command()
@click.option("--url", "-u", help="weekseries.info URL or direct m3u8 stream")
@click.option("--encoded", "-e", help="Base64 encoded stream URL")
@click.option(
    "--output",
    "-o",
    default="video.mp4",
    help="Output filename (default: automatically generated based on URL)",
)
@click.option(
    "--referer",
    "-r",
    help="Referer page URL (default: https://www.weekseries.info/)",
)
@click.option("--no-convert", is_flag=True, help="Do not convert to MP4, keep .ts only")
@click.version_option(version="0.1.0", prog_name="weekseries-dl")
def main(url, encoded, output, referer, no_convert):
    """
    WeekSeries Downloader - Download videos from WeekSeries using pure Python

    Examples:

    \b
    # Download with automatic name based on URL (NEW):
    weekseries-dl --url "https://www.weekseries.info/series/the-good-doctor/temporada-1/episodio-01"
    # Result: the_good_doctor_S01E01.mp4

    \b
    # Download using base64 encoded URL:
    weekseries-dl --encoded "aHR0cHM6Ly9zZXJpZXMudmlkbWFuaWl4LnNob3AvVC90aGUtZ29vZC1kb2N0b3IvMDItdGVtcG9yYWRhLzE2L3N0cmVhbS5tM3U4"

    \b
    # Download using direct streaming URL:
    weekseries-dl --url "https://series.vidmaniix.shop/T/the-good-doctor/02-temporada/16/stream.m3u8"
    # Result: the_good_doctor_02_temporada_16.mp4

    \b
    # With custom filename:
    weekseries-dl --url "https://www.weekseries.info/series/..." --output "my_episode.mp4"

    \b
    # Keep only .ts file (no conversion):
    weekseries-dl --url "..." --no-convert
    # Result: automatic_name.ts
    """

    # Setup logging
    LoggingConfig.setup_default()

    # Process URL using functional pattern
    stream_url, error, auto_referer, episode_info = process_url_input(url, encoded)

    if error:
        click.echo(f"Error: {error}", err=True)
        click.echo("\nSupported formats:")
        click.echo("  - weekseries.info URLs: https://www.weekseries.info/series/[series]/temporada-[number]/episodio-[number]")
        click.echo("  - Direct streaming URLs: https://example.com/stream.m3u8")
        click.echo("  - Base64 encoded URLs")
        click.echo("\nUse --help to see complete examples")
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
        click.echo(f"Download completed: {output_path}")
    else:
        click.echo("Download failed", err=True)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
