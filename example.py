#!/usr/bin/env python3
"""
Example usage of WeekSeries Downloader as a library
"""

from weekseries_downloader.downloader import download_hls_video
from weekseries_downloader.utils import decode_base64_url, sanitize_filename
from weekseries_downloader.url_detector import detect_url_type, UrlType, validate_weekseries_url
from weekseries_downloader.extractor import extract_stream_url, create_extraction_dependencies


def main():
    # Example 1: Using weekseries.info URL (NEW)
    print("=== Example 1: WeekSeries.info URL ===")
    weekseries_url = "https://www.weekseries.info/series/the-good-doctor/temporada-1/episodio-01"

    # Detect URL type
    url_type = detect_url_type(weekseries_url)
    print(f"URL type detected: {url_type}")

    if url_type == UrlType.WEEKSERIES:
        # Extract streaming URL
        dependencies = create_extraction_dependencies()
        result = extract_stream_url(weekseries_url, **dependencies)

        if result.success:
            print(f"Streaming URL extracted: {result.stream_url}")
            print(f"Episode: {result.episode_info}")
            print(f"Referer: {result.referer_url}")

            # Download example (commented out)
            # output_file = f"{result.episode_info.filename_safe_name}.mp4"
            # success = download_hls_video(result.stream_url, output_file, referer=result.referer_url)
            # print(f"Download {'successful' if success else 'failed'}")
        else:
            print(f"Extraction failed: {result.error_message}")
    
    # Example 2: Using direct streaming URL
    print("\n=== Example 2: Direct Streaming URL ===")
    direct_url = "https://example.com/stream.m3u8"  # Replace with actual URL
    url_type = detect_url_type(direct_url)
    print(f"URL type detected: {url_type}")

    if url_type == UrlType.DIRECT_STREAM:
        print("Direct URL detected, can use directly for download")
        # success = download_hls_video(direct_url, "direct_video.mp4")
        # print(f"Download {'successful' if success else 'failed'}")

    # Example 3: Using base64 encoded URL
    print("\n=== Example 3: Base64 URL ===")
    encoded_url = "aHR0cHM6Ly9leGFtcGxlLmNvbS9zdHJlYW0ubTN1OA=="  # example
    url_type = detect_url_type(encoded_url)
    print(f"URL type detected: {url_type}")

    if url_type == UrlType.BASE64:
        decoded_url = decode_base64_url(encoded_url)
        print(f"Decoded URL: {decoded_url}")
    
    # Example 4: URL validation
    print("\n=== Example 4: URL Validation ===")
    test_urls = [
        "https://www.weekseries.info/series/the-good-doctor/temporada-1/episodio-01",
        "https://example.com/stream.m3u8",
        "aHR0cHM6Ly9leGFtcGxlLmNvbS9zdHJlYW0ubTN1OA==",
        "https://invalid-url.com"
    ]

    for test_url in test_urls:
        url_type = detect_url_type(test_url)
        is_weekseries = validate_weekseries_url(test_url)
        print(f"URL: {test_url[:50]}...")
        print(f"  Type: {url_type}")
        print(f"  Is WeekSeries: {is_weekseries}")
        print()

    # Example 5: Filename sanitization
    print("=== Example 5: Sanitization ===")
    unsafe_filename = 'Series: "The Good Doctor" - S02E16.mp4'
    safe_filename = sanitize_filename(unsafe_filename)
    print(f"Original name: {unsafe_filename}")
    print(f"Sanitized name: {safe_filename}")


if __name__ == "__main__":
    main()