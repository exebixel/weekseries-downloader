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

    def cleanup(self, temp_dir: Optional[Path] = None, temp_file: Optional[Path] = None, state_file: Optional[Path] = None) -> None:
        """
        Clean up temporary files, directories, and state files

        Args:
            temp_dir: Temporary directory to remove
            temp_file: Temporary file to remove
            state_file: State file to remove (.download_state.json)
        """
        try:
            if temp_dir and temp_dir.exists():
                shutil.rmtree(temp_dir)
                self.logger.debug(f"Removed temp directory: {temp_dir}")

            if temp_file and temp_file.exists():
                temp_file.unlink()
                self.logger.debug(f"Removed temp file: {temp_file}")

            if state_file and state_file.exists():
                state_file.unlink()
                self.logger.debug(f"Removed state file: {state_file}")

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

    def append_segment_to_file(self, segment_data: bytes, output_file: Path) -> bool:
        """
        Atomically append segment data to output file

        Uses atomic operations to ensure data integrity:
        1. Write segment to temporary file
        2. Append temp file to output file
        3. Verify append with size check
        4. Delete temp file

        Args:
            segment_data: Segment binary data to append
            output_file: Output file path to append to

        Returns:
            True if successful, False otherwise
        """
        temp_file = None
        try:
            # Step 1: Write segment to temporary file
            temp_file = output_file.parent / f".tmp_segment_{output_file.stem}.ts"
            temp_file.write_bytes(segment_data)
            self.logger.debug(f"Wrote segment to temp file: {temp_file}")

            # Get current file size before append
            size_before = self.get_file_size(output_file)

            # Step 2: Append temp file to output file
            with open(output_file, "ab") as outfile:
                outfile.write(temp_file.read_bytes())

            # Step 3: Verify append with size check
            size_after = self.get_file_size(output_file)
            expected_size = size_before + len(segment_data)

            if size_after != expected_size:
                self.logger.error(f"Size mismatch after append: expected {expected_size}, got {size_after}")
                return False

            self.logger.debug(f"Successfully appended {len(segment_data)} bytes to {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error appending segment to file: {e}")
            return False

        finally:
            # Step 4: Delete temp file
            if temp_file and temp_file.exists():
                try:
                    temp_file.unlink()
                    self.logger.debug(f"Deleted temp file: {temp_file}")
                except Exception as e:
                    self.logger.warning(f"Error deleting temp file {temp_file}: {e}")

    def get_file_size(self, file_path: Path) -> int:
        """
        Get file size in bytes

        Args:
            file_path: Path to file

        Returns:
            File size in bytes, 0 if file doesn't exist
        """
        try:
            if file_path.exists():
                return file_path.stat().st_size
            return 0
        except Exception as e:
            self.logger.warning(f"Error getting file size for {file_path}: {e}")
            return 0

    def validate_partial_file(self, file_path: Path, expected_size: int) -> bool:
        """
        Validate partial file size matches expected size

        Args:
            file_path: Path to file to validate
            expected_size: Expected file size in bytes

        Returns:
            True if file exists and size matches expected, False otherwise
        """
        if not file_path.exists():
            self.logger.warning(f"File does not exist: {file_path}")
            return False

        actual_size = self.get_file_size(file_path)

        if actual_size != expected_size:
            self.logger.warning(f"File size mismatch: expected {expected_size} bytes, got {actual_size} bytes")
            return False

        self.logger.debug(f"File validation successful: {file_path} ({actual_size} bytes)")
        return True
