"""
Data classes for weekseries downloader
"""

import re
import time
from dataclasses import dataclass
from typing import Optional, Any, Dict, List


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


# Series processing data classes


@dataclass
class EpisodeLink:
    """Represents a link to a single episode"""

    url: str  # Relative URL path (e.g., /series/name/temporada-1/episodio-01)
    season: int
    episode: int
    full_url: str  # Absolute URL with domain

    def __str__(self) -> str:
        """User-friendly string representation"""
        return f"S{self.season:02d}E{self.episode:02d}"


@dataclass
class SeriesInfo:
    """Information about a TV series"""

    series_name: str
    series_url: str
    total_episodes: int
    seasons: Dict[int, List[EpisodeLink]]  # season_num -> episodes

    def get_episodes(self, season_filter: Optional[int] = None) -> List[EpisodeLink]:
        """Get episodes, optionally filtered by season"""
        if season_filter is None:
            # Return all episodes from all seasons
            all_episodes = []
            for season_num in sorted(self.seasons.keys()):
                all_episodes.extend(self.seasons[season_num])
            return all_episodes

        # Return episodes from specific season
        return self.seasons.get(season_filter, [])

    def __str__(self) -> str:
        """User-friendly string representation"""
        return f"{self.series_name} - {len(self.seasons)} seasons, {self.total_episodes} episodes"


@dataclass
class BatchDownloadConfig:
    """Configuration for batch downloads"""

    series_info: SeriesInfo
    season_filter: Optional[int]
    output_dir: str
    convert_to_mp4: bool = False
    continue_on_error: bool = True
    max_concurrent: int = 1  # Sequential by default


@dataclass
class EpisodeDownloadResult:
    """Result of downloading a single episode"""

    episode_link: EpisodeLink
    success: bool
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    duration_seconds: float = 0.0

    def __str__(self) -> str:
        """User-friendly string representation"""
        status = "✓" if self.success else "✗"
        return f"{status} {self.episode_link} - {self.output_path or self.error_message}"


@dataclass
class BatchDownloadResult:
    """Result of batch download operation"""

    total_episodes: int
    successful: int
    failed: int
    skipped: int
    results: List[EpisodeDownloadResult]
    total_duration_seconds: float

    def __str__(self) -> str:
        """User-friendly string representation"""
        return f"Downloaded {self.successful}/{self.total_episodes} episodes (Failed: {self.failed}, Skipped: {self.skipped})"
