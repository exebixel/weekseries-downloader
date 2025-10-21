# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WeekSeries Downloader is a Python CLI tool for downloading videos from WeekSeries using pure Python (no ffmpeg dependency for download, only for optional conversion). It downloads HLS (m3u8) streams and can extract streaming URLs from weekseries.info pages.

## Development Commands

### Setup
```bash
# Configure Poetry to use local .venv (recommended)
poetry config virtualenvs.in-project true

# Install dependencies (including dev dependencies)
poetry install

# Activate virtual environment
poetry shell
```

### Testing
```bash
# Run all tests with coverage
pytest -v --cov=weekseries_downloader --cov-report=xml --cov-report=term-missing

# Run tests in parallel (faster)
pytest -n auto

# Run specific test file
pytest tests/test_downloader.py

# Run specific test
pytest tests/test_downloader.py::test_function_name

# Run tests matching pattern
pytest -k "test_download"
```

### Code Quality
```bash
# Format code (auto-fix)
black weekseries_downloader/

# Check formatting without changes
black --check weekseries_downloader/

# Lint code
flake8 weekseries_downloader/ --max-line-length=150

# Run all quality checks (as in CI)
black --check weekseries_downloader/ && flake8 weekseries_downloader/ --max-line-length=150
```

### Running the CLI
```bash
# After poetry install, use the CLI command
weekseries-dl --help

# Run directly with Poetry
poetry run weekseries-dl --url "https://www.weekseries.info/series/..."

# Test CLI commands
weekseries-dl --version
weekseries-dl --help
```

## Architecture

### Core Components

The codebase follows a **functional programming approach** with **dependency injection** and uses **early returns** for cleaner control flow.

#### 1. URL Processing Pipeline (cli.py → url_detector.py → extractor.py)
- **cli.py**: Entry point that orchestrates the download flow
- **url_detector.py**: Pure functions to detect URL types (weekseries, direct stream, base64)
- **extractor.py**: Extracts streaming URLs from weekseries.info pages using dependency injection pattern with Protocol classes

#### 2. Download Pipeline (downloader.py → converter.py)
- **downloader.py**: Core HLS video download logic
  - Downloads m3u8 playlists
  - Handles master playlists (multiple qualities)
  - Downloads video segments in sequence
  - Concatenates segments into single .ts file
- **converter.py**: Optional ffmpeg conversion from .ts to .mp4

#### 3. Supporting Modules
- **models.py**: Data classes (EpisodeInfo, ExtractionResult, DownloadConfig)
- **cache.py**: In-memory cache for extracted streaming URLs
- **filename_generator.py**: Generates safe filenames from URLs/episode info
- **logging_config.py**: Structured logging configuration
- **utils.py**: Utility functions (base64 decode, sanitize filenames, create HTTP requests)
- **exceptions.py**: Custom exception classes

### Design Patterns

#### Dependency Injection via Protocols
The extractor module uses Protocol classes (Python's structural typing) for dependency injection:
```python
# Define protocols for dependencies
class HttpClient(Protocol):
    def fetch(self, url: str, headers: dict) -> Optional[str]: ...

# Inject dependencies at call time
extract_stream_url(
    page_url,
    http_client=UrllibHttpClient(),
    html_parser=RegexHtmlParser(),
    base64_decoder=StandardBase64Decoder(),
    url_validator=validate_weekseries_url
)
```

#### Early Returns
All functions use early returns to handle edge cases first, keeping the happy path at the base indentation level:
```python
def process_data(data: str) -> Result:
    if not data:
        return error_result("No data")

    if not is_valid(data):
        return error_result("Invalid data")

    # Happy path at base level
    return success_result(data)
```

#### Pure Functions
Most functions are pure (no side effects) and return new values rather than mutating state:
- All functions in `url_detector.py`
- Most utility functions in `utils.py`
- Data transformation functions throughout

### Testing Structure

Tests are organized to match the module structure:
- `tests/test_*.py` files correspond to `weekseries_downloader/*.py` modules
- `tests/conftest.py` contains shared fixtures
- Uses pytest, pytest-mock, pytest-cov, pytest-xdist, and hypothesis
- Comprehensive fixtures for EpisodeInfo, ExtractionResult, URLs, mock HTTP responses

Current test coverage: 52% (256 tests)

### Configuration

- **pyproject.toml**: Poetry dependencies, scripts, Black/Flake8 config
  - Python ^3.10 required
  - Line length: 150 characters
  - CLI entry point: `weekseries-dl` → `weekseries_downloader.cli:main`

- **Black configuration**: line-length=150, target py310
- **Flake8 configuration**: max-line-length=150, ignore E203, W503

## Important Notes

### URL Processing Flow
1. User provides URL via `--url`, `--encoded`, or weekseries.info page
2. `url_detector.detect_url_type()` identifies URL type
3. For weekseries URLs: `extractor.extract_stream_url()` fetches page and extracts base64-encoded stream URL
4. Cache is checked first to avoid re-extraction
5. Episode info is extracted for automatic filename generation

### Filename Generation
- If no `--output` specified, generates filename from URL or episode info
- Pattern: `series_name_S##E##.mp4` for weekseries URLs
- Falls back to sanitized URL patterns for direct stream URLs

### Video Download Process
1. Download m3u8 playlist
2. If master playlist (multiple qualities), select first quality
3. Parse segment URLs from playlist
4. Download segments to temp directory (`.tmp_<output_name>/`)
5. Concatenate segments into single .ts file
6. Optionally convert to .mp4 with ffmpeg
7. Clean up temporary files

### Logging
- Structured logging via `logging_config.py`
- Configuration in `logging.conf`
- Logs written to `logs/` directory
- See `LOGGING.md` for details

## CI/CD

GitHub Actions workflows:
- **ci.yml**: Runs tests on Python 3.10, 3.11, 3.12 with coverage, linting, formatting checks
- **release.yml**: (exists but not analyzed in detail)

Tests must pass with:
- pytest with coverage
- flake8 linting
- black formatting check
- CLI smoke tests (--help, --version)