"""
Data classes for weekseries downloader
"""

import re
import time
from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class EpisodeInfo:
    """Information extracted from episode URL"""

    series_name: str
    season: int
    episode: int
    original_url: str

    def __str__(self) -> str:
        """User-friendly string representation"""
        return f"{self.series_name} - S{self.season:02d}E{self.episode:02d}"

    @property
    def filename_safe_name(self) -> str:
        """Safe name for use in filenames"""
        safe_name = re.sub(r'[<>:"/\\|?*]', "_", self.series_name)
        return f"{safe_name}_S{self.season:02d}E{self.episode:02d}"


@dataclass
class ExtractionResult:
    """Result of streaming URL extraction"""

    success: bool
    stream_url: Optional[str] = None
    error_message: Optional[str] = None
    referer_url: Optional[str] = None
    episode_info: Optional[EpisodeInfo] = None

    def __bool__(self) -> bool:
        """Allow usage in boolean contexts"""
        return self.success


@dataclass
class BufferedSegment:
    """A downloaded segment waiting to be written"""

    index: int
    data: bytes
    size: int


@dataclass
class CacheEntry:
    """Cache entry with timestamp"""

    value: Any
    timestamp: float
    ttl: float  # Time to live in seconds

    @property
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        return time.time() > (self.timestamp + self.ttl)
