"""
Thread-safe buffer for downloaded HLS segments
"""

from dataclasses import dataclass
from typing import Optional, Dict
from threading import Lock
import logging


@dataclass
class BufferedSegment:
    """A downloaded segment waiting to be written"""

    index: int
    data: bytes
    size: int


class SegmentBuffer:
    """
    Thread-safe buffer for downloaded segments

    Manages in-memory storage of downloaded segments before writing to disk.
    Ensures segments are retrieved in correct order.
    """

    def __init__(self, max_buffer_size: int = 50):
        """
        Initialize segment buffer

        Args:
            max_buffer_size: Maximum number of segments to buffer in memory
        """
        self.buffer: Dict[int, BufferedSegment] = {}
        self.max_size = max_buffer_size
        self.lock = Lock()
        self.logger = logging.getLogger(__name__)

    def add_segment(self, segment: BufferedSegment) -> bool:
        """
        Add segment to buffer (thread-safe)

        Args:
            segment: Segment to add to buffer

        Returns:
            True if added, False if buffer is full
        """
        with self.lock:
            if len(self.buffer) >= self.max_size:
                return False
            self.buffer[segment.index] = segment
            return True

    def get_next_segment(self, expected_index: int) -> Optional[BufferedSegment]:
        """
        Get next segment in sequence (thread-safe)

        Args:
            expected_index: The segment index we're waiting for

        Returns:
            BufferedSegment if available, None if not yet downloaded
        """
        with self.lock:
            return self.buffer.pop(expected_index, None)

    def is_full(self) -> bool:
        """
        Check if buffer is at capacity

        Returns:
            True if buffer is full, False otherwise
        """
        with self.lock:
            return len(self.buffer) >= self.max_size

    def size(self) -> int:
        """
        Get current buffer size

        Returns:
            Number of segments currently in buffer
        """
        with self.lock:
            return len(self.buffer)

    def get_memory_usage(self) -> int:
        """
        Get approximate memory usage in bytes

        Returns:
            Total size of all buffered segments in bytes
        """
        with self.lock:
            return sum(seg.size for seg in self.buffer.values())
