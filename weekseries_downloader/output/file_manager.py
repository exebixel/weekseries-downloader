"""
File management for temporary files and directories
"""

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

        Args:
            output_path: Output file path

        Returns:
            Path to temporary directory
        """
        temp_dir = output_path.parent / f".tmp_{output_path.stem}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        self.logger.debug(f"Created temp directory: {temp_dir}")
        return temp_dir

    def concatenate_segments(self, segment_dir: Path, output_file: Path) -> bool:
        """
        Concatenate all segments in directory into single file

        Segments are concatenated in sorted order (segment_00001.ts, segment_00002.ts, ...)

        Args:
            segment_dir: Directory containing segments
            output_file: Output file path

        Returns:
            True if successful
        """
        try:
            self.logger.info("Concatenating segments...")

            # Get all segment files sorted
            segment_files = sorted(segment_dir.glob("segment_*.ts"))

            if not segment_files:
                self.logger.error(f"No segments found in {segment_dir}")
                return False

            # Ensure parent directory exists
            self.ensure_parent_dir(output_file)

            # Concatenate all segments
            with open(output_file, "wb") as outfile:
                for segment_file in segment_files:
                    outfile.write(segment_file.read_bytes())

            self.logger.info(f"Segments concatenated into: {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error concatenating segments: {e}")
            return False

    def cleanup(self, temp_dir: Optional[Path] = None, temp_file: Optional[Path] = None) -> None:
        """
        Clean up temporary files and directories

        Args:
            temp_dir: Temporary directory to remove
            temp_file: Temporary file to remove
        """
        try:
            if temp_dir and temp_dir.exists():
                shutil.rmtree(temp_dir)
                self.logger.debug(f"Removed temp directory: {temp_dir}")

            if temp_file and temp_file.exists():
                temp_file.unlink()
                self.logger.debug(f"Removed temp file: {temp_file}")

        except Exception as e:
            self.logger.warning(f"Error during cleanup: {e}")

    def cleanup_segments(self, segment_files: List[Path], temp_dir: Optional[Path] = None) -> None:
        """
        Clean up segment files and temp directory

        Args:
            segment_files: List of segment files to remove
            temp_dir: Temporary directory to remove
        """
        try:
            # Remove segment files
            for segment_file in segment_files:
                if segment_file.exists():
                    segment_file.unlink()

            self.logger.debug(f"Removed {len(segment_files)} segment files")

            # Remove temp directory
            if temp_dir and temp_dir.exists():
                temp_dir.rmdir()
                self.logger.debug(f"Removed temp directory: {temp_dir}")

        except Exception as e:
            self.logger.warning(f"Error cleaning up segments: {e}")

    @staticmethod
    def ensure_parent_dir(file_path: Path) -> None:
        """
        Ensure parent directory exists

        Args:
            file_path: File path to check
        """
        file_path.parent.mkdir(parents=True, exist_ok=True)

    def save_segment(self, segment_data: bytes, segment_dir: Path, segment_index: int) -> Optional[Path]:
        """
        Save segment data to file

        Args:
            segment_data: Segment binary data
            segment_dir: Directory to save segment
            segment_index: Segment index (1-based)

        Returns:
            Path to saved segment file or None if failed
        """
        try:
            segment_file = segment_dir / f"segment_{segment_index:05d}.ts"
            segment_file.write_bytes(segment_data)
            return segment_file

        except Exception as e:
            self.logger.error(f"Error saving segment {segment_index}: {e}")
            return None
