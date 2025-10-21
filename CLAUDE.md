# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WeekSeries Downloader is a Python CLI tool for downloading videos from WeekSeries using pure Python (no ffmpeg dependency for download, only for optional conversion). It downloads HLS (m3u8) streams and can extract streaming URLs from weekseries.info pages.

## Development Commands

**IMPORTANT: Always use Poetry to run Python commands in this project.**

### Setup
```bash
# Configure Poetry to use local .venv (recommended)
poetry config virtualenvs.in-project true

# Install dependencies (including dev dependencies)
poetry install

# Activate virtual environment (optional, but recommended for interactive work)
poetry shell
```

### Testing
```bash
# Run all tests with coverage (use Poetry)
poetry run pytest -v --cov=weekseries_downloader --cov-report=xml --cov-report=term-missing

# Run tests in parallel (faster)
poetry run pytest -n auto

# Run specific test file
poetry run pytest tests/test_downloader.py

# Run specific test
poetry run pytest tests/test_downloader.py::test_function_name

# Run tests matching pattern
poetry run pytest -k "test_download"
```

### Code Quality
```bash
# Format code (auto-fix) - use Poetry
poetry run black weekseries_downloader/

# Check formatting without changes
poetry run black --check weekseries_downloader/

# Lint code - use Poetry
poetry run flake8 weekseries_downloader/ --max-line-length=150

# Run all quality checks (as in CI)
poetry run black --check weekseries_downloader/ && poetry run flake8 weekseries_downloader/ --max-line-length=150
```

### Running the CLI
```bash
# Run with Poetry (recommended)
poetry run weekseries-dl --help
poetry run weekseries-dl --url "https://www.weekseries.info/series/..."

# Or after 'poetry shell', use directly
weekseries-dl --help
weekseries-dl --version
```

### Running Python Scripts
```bash
# Always use Poetry to run Python commands
poetry run python script.py
poetry run python -m module_name
poetry run python -c "print('test')"
```

## Architecture

### Module Structure

The codebase follows a **modular class-based architecture** with **dependency injection** and uses **early returns** for cleaner control flow. The code is organized into domain-specific packages:

```
weekseries_downloader/
├── __init__.py                 # Package initialization
├── cli.py                      # CLI entry point and orchestration
├── models.py                   # Data classes (EpisodeInfo, ExtractionResult, DownloadConfig)
├── exceptions.py               # Custom exception classes
│
├── infrastructure/             # Cross-cutting concerns
│   ├── __init__.py
│   ├── config.py              # LoggingConfig, AppConfig classes
│   ├── cache_manager.py       # CacheManager class (TTL cache)
│   ├── http_client.py         # HTTPClient class
│   └── parsers.py             # HTMLParser, Base64Parser classes
│
├── url_processing/            # URL handling domain
│   ├── __init__.py
│   ├── url_parser.py          # URLParser class (static methods)
│   └── url_extractor.py       # URLExtractor class (DI-based)
│
├── output/                    # File management domain
│   ├── __init__.py
│   ├── filename_generator.py  # FilenameGenerator class
│   └── file_manager.py        # FileManager class
│
└── download/                  # Download pipeline domain
    ├── __init__.py
    ├── playlist_parser.py     # PlaylistParser class
    ├── segment_downloader.py  # SegmentDownloader class
    ├── segment_buffer.py      # SegmentBuffer class (memory-efficient buffering)
    ├── media_converter.py     # MediaConverter class
    └── hls_downloader.py      # HLSDownloader orchestrator class
```

### Core Components

#### 1. URL Processing Pipeline (url_processing/)
- **URLParser**: Static methods for URL detection and validation (detect_url_type, is_weekseries_url, extract_episode_info)
- **URLExtractor**: Instance-based class with DI for extracting streaming URLs from weekseries.info pages

#### 2. Download Pipeline (download/)
- **HLSDownloader**: Main orchestrator that coordinates the entire download process
- **PlaylistParser**: Parses m3u8 playlists and handles master playlists (multiple qualities)
- **SegmentDownloader**: Downloads individual HLS segments with progress tracking
- **SegmentBuffer**: Memory-efficient buffering for segment data during download
- **MediaConverter**: Optional ffmpeg conversion from .ts to .mp4

#### 3. Output Management (output/)
- **FilenameGenerator**: Intelligent filename generation from URLs and episode info
- **FileManager**: Manages temporary files, segment concatenation, and cleanup

#### 4. Infrastructure (infrastructure/)
- **HTTPClient**: Handles all HTTP requests with configurable headers and retry logic
- **CacheManager**: In-memory TTL cache for extracted URLs
- **HTMLParser**: Parses HTML/JavaScript for base64-encoded URLs
- **Base64Parser**: Base64 encoding/decoding utilities (part of parsers.py)
- **LoggingConfig**: Centralized logging configuration
- **AppConfig**: Application-wide configuration constants

### Design Patterns

#### Dependency Injection with Classes
The architecture uses class-based dependency injection for testability and flexibility:
```python
# Classes accept dependencies via constructor
class URLExtractor:
    def __init__(
        self,
        http_client: Optional[HTTPClient] = None,
        html_parser: Optional[HTMLParser] = None,
        cache_manager: Optional[CacheManager] = None
    ):
        self.http_client = http_client or HTTPClient()
        self.html_parser = html_parser or HTMLParser()
        self.cache = cache_manager or CacheManager()

    @classmethod
    def create_default(cls) -> 'URLExtractor':
        """Factory method with default dependencies"""
        return cls()

# Usage
extractor = URLExtractor.create_default()
result = extractor.extract_stream_url(page_url)
```

#### Hybrid Approach (Static + Instance Methods)
Classes use a hybrid approach based on complexity:
- **Static methods** for pure utilities (URLParser, Base64Parser)
- **Instance methods** for complex operations requiring state or DI (URLExtractor, HLSDownloader, SegmentDownloader)

```python
# Static methods for pure functions
URLParser.detect_url_type(url)  # No state needed
URLParser.is_weekseries_url(url)

# Instance methods for complex operations
downloader = HLSDownloader.create_default()
downloader.download(stream_url, output_path)  # Uses injected dependencies
```

#### Early Returns
All methods use early returns to handle edge cases first, keeping the happy path at the base indentation level:
```python
def extract_stream_url(self, page_url: str) -> ExtractionResult:
    if not URLParser.is_weekseries_url(page_url):
        return ExtractionResult(success=False, error_message="Invalid URL")

    if cached_result := self.cache.get(page_url):
        return cached_result

    # Happy path at base level
    content = self.http_client.fetch(page_url)
    ...
```

### Testing Structure

Tests are organized to match the module structure:
- `tests/test_*.py` files correspond to module structure
- `tests/conftest.py` contains shared fixtures
- Uses pytest, pytest-mock, pytest-cov, pytest-xdist, and hypothesis
- Comprehensive fixtures for EpisodeInfo, ExtractionResult, URLs, mock HTTP responses

Test files updated for new architecture:
- `test_url_detector.py` → Tests URLParser static methods
- `test_filename_generator.py` → Tests FilenameGenerator instance methods
- `test_cache.py` → Tests CacheManager with TTL
- `test_converter.py` → Tests MediaConverter
- `test_exceptions.py` → Tests custom exception classes
- `test_models.py` → Tests data classes

Current test coverage: 52% (149 passing tests)

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
2. `URLParser.detect_url_type()` identifies URL type
3. For weekseries URLs: `URLExtractor.extract_stream_url()` fetches page and extracts base64-encoded stream URL
4. CacheManager is checked first to avoid re-extraction
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
- Structured logging via `infrastructure/config.py` (LoggingConfig class)
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