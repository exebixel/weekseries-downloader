"""
Data classes for weekseries downloader
"""

import re
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


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

    @property
    def is_error(self) -> bool:
        """Check if an error occurred"""
        return not self.success

    @property
    def has_stream_url(self) -> bool:
        """Check if streaming URL is present"""
        return self.success and self.stream_url is not None


@dataclass
class DownloadConfig:
    """Download configuration"""

    stream_url: str
    output_file: str
    referer_url: Optional[str] = None
    convert_to_mp4: bool = True

    @property
    def has_referer(self) -> bool:
        """Check if referer is configured"""
        return self.referer_url is not None


@dataclass
class DownloadState:
    """Track download progress for resume capability"""

    stream_url: str
    output_path: str
    total_segments: int
    completed_segments: List[int]
    file_size: int
    checksum: Optional[str]
    last_updated: str
    playlist_content: str
    base_url: str

    def to_json(self) -> dict:
        """Convert state to JSON-serializable dictionary"""
        return {
            "stream_url": self.stream_url,
            "output_path": self.output_path,
            "total_segments": self.total_segments,
            "completed_segments": self.completed_segments,
            "file_size": self.file_size,
            "checksum": self.checksum,
            "last_updated": self.last_updated,
            "playlist_content": self.playlist_content,
            "base_url": self.base_url,
        }

    @classmethod
    def from_json(cls, data: dict) -> "DownloadState":
        """Create state from JSON dictionary"""
        return cls(
            stream_url=data["stream_url"],
            output_path=data["output_path"],
            total_segments=data["total_segments"],
            completed_segments=data["completed_segments"],
            file_size=data["file_size"],
            checksum=data.get("checksum"),
            last_updated=data["last_updated"],
            playlist_content=data["playlist_content"],
            base_url=data["base_url"],
        )

    def mark_segment_complete(self, segment_index: int, new_size: int) -> None:
        """Mark a segment as completed and update file size"""
        if segment_index not in self.completed_segments:
            self.completed_segments.append(segment_index)
            self.file_size += new_size
            self.last_updated = datetime.now().isoformat()

    def is_complete(self) -> bool:
        """Check if all segments have been downloaded"""
        return len(self.completed_segments) == self.total_segments

    def get_next_segment_index(self) -> Optional[int]:
        """Get the next segment index to download (1-based)"""
        if self.is_complete():
            return None

        for i in range(1, self.total_segments + 1):
            if i not in self.completed_segments:
                return i

        return None
