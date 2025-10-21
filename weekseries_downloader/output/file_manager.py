"""
File management for temporary files and directories
"""

from pathlib import Path
import logging


class FileManager:
    """Manage temporary files and directories"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

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
