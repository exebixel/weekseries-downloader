"""
Data classes for weekseries downloader
"""

import re
from dataclasses import dataclass
from typing import Optional


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
