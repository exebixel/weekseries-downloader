# WeekSeries Downloader

A Python CLI tool for downloading videos from WeekSeries. Downloads HLS (m3u8) streams using pure Python with optional ffmpeg conversion to MP4.

## Features

- 📺 **Smart URL handling**: Direct stream URLs, base64-encoded URLs, or weekseries.info page URLs
- 🎬 **Automatic conversion**: Converts to MP4 if ffmpeg is available
- 🔄 **Quality selection**: Handles master playlists with multiple quality options
- 📝 **Intelligent naming**: Auto-generates filenames from episode information
- 🧹 **Clean operation**: Automatic temporary file cleanup
- ⚡ **Progress tracking**: Real-time download progress
- 💾 **Caching**: Remembers extracted URLs to avoid re-processing

## Installation

### Quick Install with pip

```bash
pip install git+https://github.com/exebixel/weekseries-downloader
```

### Development Installation with Poetry

```bash
# Clone the repository
git clone https://github.com/exebixel/weekseries-downloader
cd weekseries-downloader

# Configure Poetry to use local .venv (recommended)
poetry config virtualenvs.in-project true

# Install dependencies
poetry install
```

## Usage

The `weekseries-dl` command provides three ways to download videos:

### 1. WeekSeries Page URL (Recommended)

Download directly from a weekseries.info episode page - the tool will automatically extract the stream URL:

```bash
weekseries-dl --url "https://www.weekseries.info/series/the-good-doctor/temporada-2/episodio-16"
```

The output filename will be automatically generated as `the_good_doctor_S02E16.mp4`

### 2. Direct Stream URL

Use the direct m3u8 stream URL:

```bash
weekseries-dl --url "https://series.vidmaniix.shop/T/the-good-doctor/02-temporada/16/stream.m3u8"
```

### 3. Base64-Encoded URL

Use a base64-encoded stream URL:

```bash
weekseries-dl --encoded "aHR0cHM6Ly9zZXJpZXMudmlkbWFuaWl4LnNob3AvVC90aGUtZ29vZC1kb2N0b3IvMDItdGVtcG9yYWRhLzE2L3N0cmVhbS5tM3U4"
```

### Advanced Options

```bash
# Specify custom output filename
weekseries-dl --url "..." --output "my-episode.mp4"

# Skip MP4 conversion (keep .ts format)
weekseries-dl --url "..." --no-convert

# Provide custom referer header
weekseries-dl --url "..." --referer "https://www.weekseries.info/..."

# Show version
weekseries-dl --version

# Show help
weekseries-dl --help
```

### CLI Options

| Option | Short | Description |
|--------|-------|-------------|
| `--url` | `-u` | WeekSeries page URL, direct m3u8 URL, or stream URL |
| `--encoded` | `-e` | Base64-encoded stream URL |
| `--output` | `-o` | Output filename (default: auto-generated) |
| `--referer` | `-r` | Custom referer header for requests |
| `--no-convert` | | Keep .ts format, skip MP4 conversion |
| `--version` | | Show version information |
| `--help` | | Show help message |

## Optional Dependencies

### FFmpeg (For MP4 conversion)

The script can download videos without ffmpeg, but to automatically convert from .ts to .mp4:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

## How It Works

1. **URL Processing**: Detects URL type and extracts stream URL (from weekseries.info pages if needed)
2. **Playlist Download**: Fetches the m3u8 playlist containing segment URLs
3. **Quality Selection**: Chooses quality level from master playlist if available
4. **Segment Download**: Downloads all .ts video segments with progress tracking
5. **Concatenation**: Joins segments into a single .ts file
6. **Conversion**: Optionally converts to .mp4 using ffmpeg (if available)
7. **Cleanup**: Removes temporary files automatically

## Development

For development setup and detailed architecture information, see `CLAUDE.md`.

Quick start:
```bash
# Install with dev dependencies
poetry install

# Run tests
pytest

# Format and lint
black weekseries_downloader/
flake8 weekseries_downloader/
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Disclaimer

This script is for educational purposes only. Make sure you have permission to download the content and respect the terms of use of the websites.
