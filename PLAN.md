# WeekSeries Downloader - Refactoring Plan

**Date:** 2025-10-20
**Approach:** Hybrid class-based architecture (Option C)
**Migration:** All at once
**Goal:** Modular structure with clear separation of concerns and easy extensibility

---

## 🎯 Objectives

1. **Modularize** the codebase into logical domain packages
2. **Class-based organization** with hybrid approach (static + instance methods)
3. **Maintain testability** and dependency injection benefits
4. **Improve extensibility** with clear extension points
5. **Preserve functionality** - all existing features work identically

---

## 📦 New Module Structure

```
weekseries_downloader/
├── cli.py                      # [MODIFIED] Simplified orchestration
├── models.py                   # [KEEP] Data classes unchanged
├── exceptions.py               # [KEEP] Custom exceptions unchanged
│
├── url_processing/             # [NEW] URL handling domain
│   ├── __init__.py
│   ├── url_parser.py           # URLParser class
│   ├── url_extractor.py        # URLExtractor class
│   └── url_decoder.py          # URLDecoder class
│
├── download/                   # [NEW] Download domain
│   ├── __init__.py
│   ├── hls_downloader.py       # HLSDownloader class
│   ├── segment_downloader.py   # SegmentDownloader class
│   ├── playlist_parser.py      # PlaylistParser class
│   └── media_converter.py      # MediaConverter class
│
├── output/                     # [NEW] File management domain
│   ├── __init__.py
│   ├── filename_generator.py   # FilenameGenerator class
│   └── file_manager.py         # FileManager class
│
└── infrastructure/             # [NEW] Cross-cutting concerns
    ├── __init__.py
    ├── http_client.py          # HTTPClient class
    ├── parsers.py              # HTMLParser, Base64Parser classes
    ├── cache_manager.py        # CacheManager class
    └── config.py               # Config, LoggingConfig classes
```

**Files to be REMOVED after migration:**
- ❌ `url_detector.py` → migrated to `url_processing/url_parser.py`
- ❌ `extractor.py` → migrated to `url_processing/url_extractor.py`
- ❌ `downloader.py` → migrated to `download/hls_downloader.py` + `download/segment_downloader.py`
- ❌ `converter.py` → migrated to `download/media_converter.py`
- ❌ `filename_generator.py` → migrated to `output/filename_generator.py`
- ❌ `cache.py` → migrated to `infrastructure/cache_manager.py`
- ❌ `utils.py` → split across `infrastructure/http_client.py` + `url_processing/url_decoder.py`
- ❌ `logging_config.py` → migrated to `infrastructure/config.py`

---

## 🏗️ Detailed Class Design

### 1. `url_processing/url_parser.py`

**Source:** `url_detector.py` (135 LOC)

```python
from enum import Enum
from typing import Optional
from ..models import EpisodeInfo

class URLType(Enum):
    WEEKSERIES = "weekseries"
    DIRECT_STREAM = "direct_stream"
    BASE64 = "base64"
    UNKNOWN = "unknown"

class URLParser:
    """Parse and validate WeekSeries URLs"""

    # Static methods - Simple validation (no dependencies)
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if string is a valid HTTP(S) URL"""
        return bool(url and url.startswith(('http://', 'https://')))

    @staticmethod
    def is_weekseries_url(url: str) -> bool:
        """Check if URL is from weekseries.info"""
        # Current: validate_weekseries_url()
        pass

    @staticmethod
    def is_direct_stream_url(url: str) -> bool:
        """Check if URL is a direct m3u8/mpd stream"""
        # Current: is_direct_stream_url()
        pass

    @staticmethod
    def is_base64_encoded(url: str) -> bool:
        """Check if string is base64-encoded URL"""
        # Current: is_base64_url()
        pass

    @staticmethod
    def detect_url_type(url: str) -> URLType:
        """Detect the type of URL provided"""
        # Current: detect_url_type()
        pass

    @staticmethod
    def extract_episode_info(url: str) -> Optional[EpisodeInfo]:
        """Extract episode info from weekseries URL"""
        # Current: extract_episode_info_from_url()
        pass
```

**Migration:**
- Move all functions from `url_detector.py`
- Keep as static methods (pure functions, no state)
- Add URLType enum for type safety

---

### 2. `url_processing/url_decoder.py`

**Source:** `utils.py` (partial - 61 LOC)

```python
import base64
from typing import Optional

class URLDecoder:
    """Decode and transform URLs"""

    @staticmethod
    def decode_base64(encoded: str) -> Optional[str]:
        """Decode base64-encoded URL"""
        # Current: utils.decode_base64_url()
        pass

    @staticmethod
    def clean_url(url: str) -> str:
        """Remove URL parameters and fragments"""
        pass

    @staticmethod
    def extract_url_from_text(text: str) -> Optional[str]:
        """Extract first URL from text content"""
        pass
```

**Migration:**
- Move `decode_base64_url()` from `utils.py`
- Add helper methods for URL cleaning
- Keep as static methods (pure transformations)

---

### 3. `url_processing/url_extractor.py`

**Source:** `extractor.py` (387 LOC)

```python
from typing import Optional, Protocol
from ..models import ExtractionResult, EpisodeInfo
from ..infrastructure.http_client import HTTPClient
from ..infrastructure.parsers import HTMLParser, Base64Parser
from ..infrastructure.cache_manager import CacheManager

class URLExtractor:
    """Extract streaming URLs from WeekSeries pages"""

    def __init__(
        self,
        http_client: HTTPClient,
        html_parser: HTMLParser,
        base64_parser: Base64Parser,
        cache_manager: Optional[CacheManager] = None
    ):
        """Initialize with dependency injection"""
        self.http_client = http_client
        self.html_parser = html_parser
        self.base64_parser = base64_parser
        self.cache = cache_manager or CacheManager()

    def extract_stream_url(self, page_url: str) -> ExtractionResult:
        """
        Extract streaming URL from weekseries page

        Returns ExtractionResult with:
        - success: bool
        - stream_url: Optional[str]
        - referer_url: Optional[str]
        - episode_info: Optional[EpisodeInfo]
        - error_message: Optional[str]
        """
        # Current: extract_stream_url() with DI pattern

        # 1. Check cache first
        if cached := self.cache.get(page_url):
            return cached

        # 2. Fetch page
        content = self.http_client.fetch(page_url)
        if not content:
            return ExtractionResult(success=False, error_message="Failed to fetch page")

        # 3. Parse HTML/JS for encoded URL
        encoded_url = self.html_parser.parse_stream_url(content)
        if not encoded_url:
            return ExtractionResult(success=False, error_message="Stream URL not found")

        # 4. Decode base64
        stream_url = self.base64_parser.decode(encoded_url)
        if not stream_url:
            return ExtractionResult(success=False, error_message="Failed to decode URL")

        # 5. Extract episode info
        episode_info = URLParser.extract_episode_info(page_url)

        # 6. Build result and cache
        result = ExtractionResult(
            success=True,
            stream_url=stream_url,
            referer_url=page_url,
            episode_info=episode_info
        )
        self.cache.set(page_url, result)

        return result

    @classmethod
    def create_default(cls) -> 'URLExtractor':
        """Factory method with default dependencies"""
        from ..infrastructure.http_client import DefaultHTTPClient
        from ..infrastructure.parsers import RegexHTMLParser, StandardBase64Parser

        return cls(
            http_client=DefaultHTTPClient(),
            html_parser=RegexHTMLParser(),
            base64_parser=StandardBase64Parser(),
            cache_manager=CacheManager()
        )
```

**Migration:**
- Migrate `extract_stream_url()` and related functions from `extractor.py`
- Convert Protocol pattern to class-based DI
- Maintain testability with injected dependencies
- Add factory method for convenience

---

### 4. `infrastructure/http_client.py`

**Source:** `utils.py` (partial) + `extractor.py` protocols

```python
from typing import Optional, Dict
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import logging

class HTTPClient:
    """HTTP client for making web requests"""

    def __init__(self, timeout: int = 30, user_agent: Optional[str] = None):
        self.timeout = timeout
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        self.logger = logging.getLogger(__name__)

    def fetch(self, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[str]:
        """
        Fetch URL content with error handling

        Returns page content or None if failed
        """
        # Current: UrllibHttpClient.fetch()
        pass

    def create_request(self, url: str, headers: Optional[Dict[str, str]] = None) -> Request:
        """Create configured urllib Request object"""
        # Current: utils.create_request()
        pass

    @staticmethod
    def get_default_headers() -> Dict[str, str]:
        """Get default HTTP headers"""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "*/*",
        }
```

**Migration:**
- Move `create_request()` from `utils.py`
- Move `UrllibHttpClient` implementation from `extractor.py`
- Instance methods with configurable timeout/headers
- Maintain logging

---

### 5. `infrastructure/parsers.py`

**Source:** `extractor.py` (partial - 387 LOC)

```python
from typing import Optional
import re
import base64
import logging

class HTMLParser:
    """Parse HTML/JavaScript content for stream URLs"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Pre-compile regex patterns for performance
        self.stream_pattern = re.compile(r'...')  # Current patterns from extractor.py

    def parse_stream_url(self, content: str) -> Optional[str]:
        """
        Parse page content to extract base64-encoded stream URL

        Tries multiple patterns:
        1. JavaScript variable assignments
        2. Embedded JSON objects
        3. iframe src attributes
        """
        # Current: RegexHtmlParser.parse_stream_url()
        pass

class Base64Parser:
    """Parse and decode base64-encoded data"""

    @staticmethod
    def decode(encoded: str) -> Optional[str]:
        """Decode base64 string with error handling"""
        # Current: StandardBase64Decoder.decode()
        pass

    @staticmethod
    def is_valid_base64(text: str) -> bool:
        """Check if string is valid base64"""
        pass
```

**Migration:**
- Move `RegexHtmlParser` and `StandardBase64Decoder` from `extractor.py`
- Keep regex compilation at instance level
- Static methods for Base64Parser (pure transformations)

---

### 6. `infrastructure/cache_manager.py`

**Source:** `cache.py` (165 LOC)

```python
from typing import Any, Optional, Dict
import time
import logging

class CacheManager:
    """In-memory TTL cache for extraction results"""

    def __init__(self, default_ttl: int = 600):
        """
        Initialize cache with TTL in seconds (default: 10 minutes)
        """
        self.default_ttl = default_ttl
        self._cache: Dict[str, tuple[Any, float]] = {}
        self.logger = logging.getLogger(__name__)

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if exists and not expired"""
        # Current: SimpleCache.get()
        pass

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        # Current: SimpleCache.set()
        pass

    def clear(self) -> None:
        """Clear all cache entries"""
        # Current: SimpleCache.clear()
        pass

    def _cleanup_expired(self) -> None:
        """Remove expired entries"""
        pass

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "entries": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
        }
```

**Migration:**
- Move `SimpleCache` from `cache.py` → `CacheManager`
- Add statistics tracking
- Keep instance-based (maintains state)

---

### 7. `infrastructure/config.py`

**Source:** `logging_config.py` (128 LOC)

```python
import logging
import logging.config
from pathlib import Path
from typing import Optional

class LoggingConfig:
    """Centralized logging configuration"""

    @staticmethod
    def setup(config_file: Optional[Path] = None, log_dir: Optional[Path] = None) -> None:
        """
        Setup logging configuration

        Args:
            config_file: Path to logging.conf (default: ./logging.conf)
            log_dir: Directory for log files (default: ./logs/)
        """
        # Current: setup_logging()
        pass

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get configured logger by name"""
        return logging.getLogger(name)

class AppConfig:
    """Application-wide configuration"""

    DEFAULT_TIMEOUT = 30
    DEFAULT_CACHE_TTL = 600
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

    @staticmethod
    def get_version() -> str:
        """Get application version from pyproject.toml"""
        pass
```

**Migration:**
- Move all logging setup from `logging_config.py`
- Add AppConfig for centralized constants
- Keep as static methods (configuration, no state)

---

### 8. `download/playlist_parser.py`

**Source:** `downloader.py` (partial - 244 LOC)

```python
from typing import List, Optional, Tuple
from urllib.parse import urljoin
import logging

class PlaylistParser:
    """Parse HLS m3u8 playlists"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def is_master_playlist(self, content: str) -> bool:
        """Check if playlist is a master playlist (multiple qualities)"""
        # Current: logic from download_hls_video()
        return '#EXT-X-STREAM-INF' in content

    def get_first_quality_url(self, content: str, base_url: str) -> Optional[str]:
        """Extract first quality variant from master playlist"""
        # Current: logic from download_hls_video()
        pass

    def parse_segments(self, content: str, base_url: str) -> List[str]:
        """
        Parse segment URLs from m3u8 playlist

        Returns list of absolute segment URLs
        """
        # Current: parse logic from download_hls_video()
        pass

    @staticmethod
    def make_absolute_url(segment: str, base_url: str) -> str:
        """Convert relative segment URL to absolute"""
        return urljoin(base_url, segment)
```

**Migration:**
- Extract playlist parsing logic from `downloader.py`
- Instance methods with logging
- Focused responsibility: parse playlists only

---

### 9. `download/segment_downloader.py`

**Source:** `downloader.py` (partial - 244 LOC)

```python
from pathlib import Path
from typing import List, Optional
import logging
from ..infrastructure.http_client import HTTPClient

class SegmentDownloader:
    """Download individual HLS segments"""

    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
        self.logger = logging.getLogger(__name__)

    def download_segments(
        self,
        segment_urls: List[str],
        output_dir: Path,
        referer: Optional[str] = None
    ) -> bool:
        """
        Download all segments to output directory

        Returns True if all segments downloaded successfully
        """
        # Current: segment download loop from download_hls_video()
        pass

    def download_single_segment(
        self,
        segment_url: str,
        output_path: Path,
        referer: Optional[str] = None
    ) -> bool:
        """Download single segment file"""
        pass
```

**Migration:**
- Extract segment download logic from `downloader.py`
- Use injected HTTPClient for requests
- Progress tracking per segment

---

### 10. `download/hls_downloader.py`

**Source:** `downloader.py` (244 LOC)

```python
from pathlib import Path
from typing import Optional
import logging
from .playlist_parser import PlaylistParser
from .segment_downloader import SegmentDownloader
from .media_converter import MediaConverter
from ..infrastructure.http_client import HTTPClient
from ..output.file_manager import FileManager

class HLSDownloader:
    """Main HLS video download orchestrator"""

    def __init__(
        self,
        http_client: Optional[HTTPClient] = None,
        playlist_parser: Optional[PlaylistParser] = None,
        segment_downloader: Optional[SegmentDownloader] = None,
        file_manager: Optional[FileManager] = None,
        media_converter: Optional[MediaConverter] = None
    ):
        """Initialize with dependency injection"""
        self.http_client = http_client or HTTPClient()
        self.playlist_parser = playlist_parser or PlaylistParser()
        self.segment_downloader = segment_downloader or SegmentDownloader(self.http_client)
        self.file_manager = file_manager or FileManager()
        self.media_converter = media_converter or MediaConverter()
        self.logger = logging.getLogger(__name__)

    def download(
        self,
        stream_url: str,
        output_path: Path,
        referer: Optional[str] = None,
        convert_to_mp4: bool = True
    ) -> bool:
        """
        Download HLS video from stream URL

        Steps:
        1. Download m3u8 playlist
        2. Check if master playlist (multiple qualities)
        3. Select first quality if master
        4. Parse segment URLs
        5. Create temp directory
        6. Download all segments
        7. Concatenate segments
        8. Convert to mp4 (optional)
        9. Cleanup temp files

        Returns True if successful
        """
        # Current: download_hls_video() orchestration

        # 1. Download playlist
        playlist_content = self.http_client.fetch(stream_url)
        if not playlist_content:
            return False

        # 2-3. Handle master playlist
        if self.playlist_parser.is_master_playlist(playlist_content):
            stream_url = self.playlist_parser.get_first_quality_url(playlist_content, stream_url)
            playlist_content = self.http_client.fetch(stream_url)

        # 4. Parse segments
        segments = self.playlist_parser.parse_segments(playlist_content, stream_url)

        # 5-6. Download segments
        temp_dir = self.file_manager.create_temp_dir(output_path)
        success = self.segment_downloader.download_segments(segments, temp_dir, referer)

        if not success:
            return False

        # 7. Concatenate
        ts_file = output_path.with_suffix('.ts')
        self.file_manager.concatenate_segments(temp_dir, ts_file)

        # 8. Convert
        if convert_to_mp4:
            self.media_converter.convert_to_mp4(ts_file, output_path)

        # 9. Cleanup
        self.file_manager.cleanup(temp_dir, ts_file if convert_to_mp4 else None)

        return True

    @classmethod
    def create_default(cls) -> 'HLSDownloader':
        """Factory method with default dependencies"""
        return cls()
```

**Migration:**
- Main orchestrator for download pipeline
- Delegates to specialized classes
- Maintains high-level flow control
- Uses DI for testability

---

### 11. `download/media_converter.py`

**Source:** `converter.py` (40 LOC)

```python
from pathlib import Path
import subprocess
import logging
from typing import Optional

class MediaConverter:
    """Convert video files using FFmpeg"""

    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path
        self.logger = logging.getLogger(__name__)

    def convert_to_mp4(
        self,
        input_file: Path,
        output_file: Path,
        overwrite: bool = True
    ) -> bool:
        """
        Convert .ts file to .mp4 using FFmpeg

        Returns True if successful
        """
        # Current: convert_to_mp4()
        pass

    def is_ffmpeg_available(self) -> bool:
        """Check if FFmpeg is installed and accessible"""
        try:
            subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def get_conversion_command(
        input_file: Path,
        output_file: Path,
        overwrite: bool = True
    ) -> list[str]:
        """Build FFmpeg command arguments"""
        cmd = ["ffmpeg"]
        if overwrite:
            cmd.append("-y")
        cmd.extend([
            "-i", str(input_file),
            "-c", "copy",
            str(output_file)
        ])
        return cmd
```

**Migration:**
- Move from `converter.py`
- Add ffmpeg availability check
- Configurable ffmpeg path
- Static method for command building

---

### 12. `output/filename_generator.py`

**Source:** `filename_generator.py` (306 LOC)

```python
from pathlib import Path
from typing import Optional
import re
import logging
from ..models import EpisodeInfo

class FilenameGenerator:
    """Generate intelligent output filenames"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Pre-compile patterns
        self._init_patterns()

    def generate(
        self,
        stream_url: str,
        episode_info: Optional[EpisodeInfo] = None,
        user_output: Optional[str] = None,
        default_extension: str = ".mp4"
    ) -> str:
        """
        Generate output filename with multiple strategies

        Priority:
        1. User-provided output (if given)
        2. Episode info (series_S##E##.mp4)
        3. Extract from stream URL patterns
        4. Fallback to "video.mp4"

        Returns sanitized filename
        """
        # Current: generate_automatic_filename() logic

        # Strategy 1: User provided
        if user_output:
            return self._ensure_extension(user_output, default_extension)

        # Strategy 2: Episode info
        if episode_info:
            return self._format_episode_filename(episode_info, default_extension)

        # Strategy 3: Extract from URL
        if extracted := self._extract_from_url(stream_url):
            return self._sanitize(extracted + default_extension)

        # Strategy 4: Fallback
        return f"video{default_extension}"

    def _format_episode_filename(self, info: EpisodeInfo, ext: str) -> str:
        """Format: series_name_S01E05.mp4"""
        pass

    def _extract_from_url(self, url: str) -> Optional[str]:
        """Try multiple URL patterns to extract filename"""
        # Current: 4 different extraction strategies
        pass

    @staticmethod
    def _sanitize(filename: str) -> str:
        """Sanitize filename for filesystem"""
        # Current: sanitize_filename() from utils.py
        pass

    @staticmethod
    def _ensure_extension(filename: str, default_ext: str) -> str:
        """Ensure filename has video extension"""
        pass
```

**Migration:**
- Move from standalone `filename_generator.py`
- Keep multi-strategy approach
- Instance methods with pattern compilation
- Static utilities for sanitization

---

### 13. `output/file_manager.py`

**New class** - extracted from `downloader.py`

```python
from pathlib import Path
from typing import List, Optional
import shutil
import logging

class FileManager:
    """Manage temporary files and directories"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_temp_dir(self, output_path: Path) -> Path:
        """
        Create temporary directory for segments

        Format: .tmp_<output_filename>/
        """
        temp_dir = output_path.parent / f".tmp_{output_path.stem}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir

    def concatenate_segments(self, segment_dir: Path, output_file: Path) -> bool:
        """
        Concatenate all segments in directory into single file

        Segments are concatenated in sorted order (001.ts, 002.ts, ...)
        """
        # Current: concatenation logic from download_hls_video()
        pass

    def cleanup(
        self,
        temp_dir: Optional[Path] = None,
        temp_file: Optional[Path] = None
    ) -> None:
        """Clean up temporary files and directories"""
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir)

        if temp_file and temp_file.exists():
            temp_file.unlink()

    @staticmethod
    def ensure_parent_dir(file_path: Path) -> None:
        """Ensure parent directory exists"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
```

**Migration:**
- Extract file operations from `downloader.py`
- Centralize temp directory management
- Cleanup logic in one place

---

### 14. `cli.py` (Modified)

**Source:** Current `cli.py` (170 LOC)

```python
import click
from pathlib import Path
from .url_processing.url_parser import URLParser, URLType
from .url_processing.url_decoder import URLDecoder
from .url_processing.url_extractor import URLExtractor
from .download.hls_downloader import HLSDownloader
from .output.filename_generator import FilenameGenerator
from .infrastructure.config import LoggingConfig, AppConfig

@click.command()
@click.option('--url', help='URL da página do WeekSeries ou URL direto do stream')
@click.option('--encoded', help='URL codificada em base64')
@click.option('--output', '-o', help='Caminho do arquivo de saída')
@click.option('--no-convert', is_flag=True, help='Não converter para MP4')
@click.version_option(version=AppConfig.get_version())
def main(url: str, encoded: str, output: str, no_convert: bool):
    """WeekSeries Downloader - Download videos from WeekSeries"""

    # Setup logging
    LoggingConfig.setup()
    logger = LoggingConfig.get_logger(__name__)

    # Process URL input
    stream_url, error, referer, episode_info = process_url_input(url, encoded)

    if error:
        click.echo(f"Erro: {error}", err=True)
        return 1

    # Generate output filename
    generator = FilenameGenerator()
    output_filename = generator.generate(
        stream_url=stream_url,
        episode_info=episode_info,
        user_output=output
    )
    output_path = Path(output_filename)

    # Download video
    downloader = HLSDownloader.create_default()
    success = downloader.download(
        stream_url=stream_url,
        output_path=output_path,
        referer=referer,
        convert_to_mp4=not no_convert
    )

    if success:
        click.echo(f"✅ Download concluído: {output_path}")
        return 0
    else:
        click.echo("❌ Falha no download", err=True)
        return 1

def process_url_input(url: str, encoded: str) -> tuple[str, str, str, EpisodeInfo]:
    """
    Process URL input and extract streaming URL

    Returns: (stream_url, error_message, referer_url, episode_info)
    """
    # Handle base64 encoded input
    if encoded:
        url = URLDecoder.decode_base64(encoded)
        if not url:
            return None, "URL codificada inválida", None, None

    # Validate URL provided
    if not url:
        return None, "Nenhuma URL fornecida", None, None

    # Detect URL type
    url_type = URLParser.detect_url_type(url)

    # Handle different URL types
    if url_type == URLType.DIRECT_STREAM:
        return url, None, None, None

    elif url_type == URLType.WEEKSERIES:
        extractor = URLExtractor.create_default()
        result = extractor.extract_stream_url(url)

        if result.success:
            return result.stream_url, None, result.referer_url, result.episode_info
        else:
            return None, result.error_message, None, None

    elif url_type == URLType.BASE64:
        decoded = URLDecoder.decode_base64(url)
        if decoded:
            return decoded, None, None, None
        else:
            return None, "Falha ao decodificar URL", None, None

    else:
        return None, "Tipo de URL não reconhecido", None, None

if __name__ == '__main__':
    main()
```

**Changes:**
- Simplified orchestration (delegates to classes)
- Clean imports from new module structure
- Maintains all existing CLI functionality
- Uses factory methods for default instances

---

## 🔄 Migration Steps

### Phase 1: Infrastructure (Foundation)
**Order:** Bottom-up (least dependencies first)

1. ✅ Create `infrastructure/` package
2. ✅ Implement `infrastructure/config.py` (from `logging_config.py`)
3. ✅ Implement `infrastructure/cache_manager.py` (from `cache.py`)
4. ✅ Implement `infrastructure/http_client.py` (from `utils.py` + `extractor.py`)
5. ✅ Implement `infrastructure/parsers.py` (from `extractor.py`)

**Dependencies:** Only stdlib and existing `models.py`, `exceptions.py`

**Testing:** Run existing tests to ensure no regressions

---

### Phase 2: URL Processing
**Dependencies:** Infrastructure + models

6. ✅ Create `url_processing/` package
7. ✅ Implement `url_processing/url_decoder.py` (from `utils.py`)
8. ✅ Implement `url_processing/url_parser.py` (from `url_detector.py`)
9. ✅ Implement `url_processing/url_extractor.py` (from `extractor.py`)

**Testing:** Port tests from `test_url_detector.py` and `test_extractor.py`

---

### Phase 3: Output Management
**Dependencies:** Models only

10. ✅ Create `output/` package
11. ✅ Implement `output/filename_generator.py` (from `filename_generator.py`)
12. ✅ Implement `output/file_manager.py` (new - from `downloader.py`)

**Testing:** Port tests from `test_filename_generator.py`

---

### Phase 4: Download Pipeline
**Dependencies:** Infrastructure + Output

13. ✅ Create `download/` package
14. ✅ Implement `download/playlist_parser.py` (from `downloader.py`)
15. ✅ Implement `download/segment_downloader.py` (from `downloader.py`)
16. ✅ Implement `download/media_converter.py` (from `converter.py`)
17. ✅ Implement `download/hls_downloader.py` (orchestrator)

**Testing:** Port tests from `test_downloader.py` and `test_converter.py`

---

### Phase 5: CLI Integration
**Dependencies:** All modules

18. ✅ Update `cli.py` with new imports and structure
19. ✅ Test CLI commands (`--help`, `--version`, sample downloads)

---

### Phase 6: Testing & Cleanup

20. ✅ Run full test suite: `pytest -v --cov=weekseries_downloader`
21. ✅ Verify coverage remains ≥52%
22. ✅ Run linting: `flake8 weekseries_downloader/ --max-line-length=150`
23. ✅ Run formatting: `black --check weekseries_downloader/`
24. ✅ Test CLI smoke tests
25. ✅ **Delete old files:**
    - `url_detector.py`
    - `extractor.py`
    - `downloader.py`
    - `converter.py`
    - `filename_generator.py`
    - `cache.py`
    - `utils.py`
    - `logging_config.py`

26. ✅ Update `__init__.py` exports if needed
27. ✅ Update documentation (README, CLAUDE.md)

---

## 📋 Testing Strategy

### Unit Tests
Each class should have corresponding test file:
```
tests/
├── test_url_processing/
│   ├── test_url_parser.py
│   ├── test_url_decoder.py
│   └── test_url_extractor.py
├── test_download/
│   ├── test_hls_downloader.py
│   ├── test_segment_downloader.py
│   ├── test_playlist_parser.py
│   └── test_media_converter.py
├── test_output/
│   ├── test_filename_generator.py
│   └── test_file_manager.py
└── test_infrastructure/
    ├── test_http_client.py
    ├── test_parsers.py
    ├── test_cache_manager.py
    └── test_config.py
```

### Integration Tests
- Test full CLI flow: URL → extraction → download → conversion
- Test error handling paths
- Test cache behavior across requests

### Migration Testing
1. Run tests after each phase
2. Ensure coverage doesn't drop below 52%
3. Run CLI smoke tests before cleanup phase

---

## 🎯 Benefits of New Architecture

### 1. **Clear Separation of Concerns**
- URL processing (parsing, validation, extraction)
- Download pipeline (playlist, segments, conversion)
- Output management (filenames, temp files)
- Infrastructure (HTTP, parsing, caching, config)

### 2. **Easy Extensibility**
Want to add new features?
- **New URL source:** Extend `URLExtractor` or create new extractor
- **New download protocol:** Create new downloader class implementing same interface
- **New output format:** Extend `MediaConverter`
- **New cache backend:** Swap `CacheManager` implementation

### 3. **Better Testability**
- Dependency injection for all complex classes
- Factory methods for default configurations
- Easy to mock HTTP, parsing, file operations
- Isolated unit tests per class

### 4. **Maintainability**
- Smaller, focused classes (vs 387-line `extractor.py`)
- Clear responsibilities per module
- Hybrid approach: static for utils, instance for complex logic
- Self-documenting code structure

### 5. **Backwards Compatibility**
- CLI interface unchanged
- All existing functionality preserved
- Same command-line options
- Same output behavior

---

## 📊 Code Size Comparison

### Before (Current)
```
cli.py                  170 LOC
extractor.py           387 LOC  ← Largest, complex DI
filename_generator.py  306 LOC
downloader.py          244 LOC
url_detector.py        135 LOC
cache.py               165 LOC
logging_config.py      128 LOC
converter.py            40 LOC
utils.py                61 LOC
models.py               63 LOC
exceptions.py           94 LOC
────────────────────────────
TOTAL               1,793 LOC
```

### After (Proposed)
```
# URL Processing (517 LOC)
url_processing/url_parser.py      135 LOC  (from url_detector.py)
url_processing/url_extractor.py   350 LOC  (from extractor.py, simplified)
url_processing/url_decoder.py      32 LOC  (from utils.py)

# Download (450 LOC)
download/hls_downloader.py        150 LOC  (orchestrator)
download/segment_downloader.py     80 LOC  (from downloader.py)
download/playlist_parser.py        90 LOC  (from downloader.py)
download/media_converter.py       130 LOC  (from converter.py, enhanced)

# Output (380 LOC)
output/filename_generator.py      310 LOC  (from filename_generator.py)
output/file_manager.py             70 LOC  (from downloader.py)

# Infrastructure (450 LOC)
infrastructure/http_client.py     120 LOC  (from utils.py + extractor.py)
infrastructure/parsers.py         140 LOC  (from extractor.py)
infrastructure/cache_manager.py   170 LOC  (from cache.py, enhanced)
infrastructure/config.py          150 LOC  (from logging_config.py, enhanced)

# Core (327 LOC)
cli.py                            170 LOC  (simplified)
models.py                          63 LOC  (unchanged)
exceptions.py                      94 LOC  (unchanged)
────────────────────────────────
TOTAL                          2,124 LOC  (+18% for better organization)
```

**Size increase justified by:**
- Better code organization
- More docstrings and type hints
- Explicit class structures
- Factory methods
- Enhanced error handling

---

## 🔍 Example Usage After Refactoring

### For CLI Users (No Change)
```bash
# Exact same commands work
weekseries-dl --url "https://weekseries.info/series/..."
weekseries-dl --encoded "aHR0cHM6Ly9..."
weekseries-dl --url "..." --output "episode.mp4" --no-convert
```

### For Developers (New API)
```python
# URL processing
from weekseries_downloader.url_processing import URLParser, URLExtractor

url_type = URLParser.detect_url_type(url)
episode_info = URLParser.extract_episode_info(url)

extractor = URLExtractor.create_default()
result = extractor.extract_stream_url(page_url)

# Download
from weekseries_downloader.download import HLSDownloader

downloader = HLSDownloader.create_default()
success = downloader.download(stream_url, output_path)

# Custom configuration with DI
from weekseries_downloader.infrastructure import HTTPClient, CacheManager

custom_http = HTTPClient(timeout=60)
custom_cache = CacheManager(default_ttl=3600)

extractor = URLExtractor(
    http_client=custom_http,
    cache_manager=custom_cache,
    # ... other dependencies
)
```

---

## ✅ Success Criteria

Migration is successful when:

1. ✅ All 256 tests pass
2. ✅ Coverage ≥ 52% maintained
3. ✅ Linting passes (flake8)
4. ✅ Formatting passes (black)
5. ✅ CLI commands work identically
6. ✅ All old files removed
7. ✅ Documentation updated
8. ✅ CI pipeline passes

---

## 🚀 Next Steps

After reviewing this plan:
1. **Approve the structure** - Any changes to module organization?
2. **Start Phase 1** - Implement infrastructure modules
3. **Incremental testing** - Run tests after each phase
4. **Review and iterate** - Adjust as needed during implementation

---

## 📚 References

- Current architecture: See CLAUDE.md
- Testing commands: See CLAUDE.md § Testing
- Code quality: See CLAUDE.md § Code Quality
- Design patterns: Dependency Injection, Factory Method, Strategy Pattern

---

**Last Updated:** 2025-10-20
**Status:** Ready for implementation