"""
Video format converter using FFmpeg
"""

from pathlib import Path
import subprocess
import logging
from typing import Optional


class MediaConverter:
    """Convert video files using FFmpeg"""

    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        """
        Initialize converter

        Args:
            ffmpeg_path: Path to ffmpeg executable
        """
        self.ffmpeg_path = ffmpeg_path
        self.logger = logging.getLogger(__name__)

    def convert_to_mp4(self, input_file: Path, output_file: Path, overwrite: bool = True) -> bool:
        """
        Convert .ts file to .mp4 using FFmpeg

        Args:
            input_file: Input .ts file path
            output_file: Output .mp4 file path
            overwrite: Whether to overwrite existing file

        Returns:
            True if successful
        """
        self.logger.info("Converting to MP4...")

        cmd = self.get_conversion_command(input_file, output_file, overwrite)

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            self.logger.info(f"Conversion complete! MP4 file: {output_file}")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error converting: {e}")
            self.logger.error(f"FFmpeg stderr: {e.stderr.decode('utf-8') if e.stderr else 'N/A'}")
            return False

        except FileNotFoundError:
            self.logger.error(f"FFmpeg not found at: {self.ffmpeg_path}")
            self.logger.error("Install ffmpeg with: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)")
            return False

    def is_ffmpeg_available(self) -> bool:
        """
        Check if FFmpeg is installed and accessible

        Returns:
            True if ffmpeg is available
        """
        try:
            subprocess.run([self.ffmpeg_path, "-version"], capture_output=True, check=True)
            return True

        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_conversion_command(self, input_file: Path, output_file: Path, overwrite: bool = True) -> list[str]:
        """
        Build FFmpeg command arguments

        Args:
            input_file: Input file path
            output_file: Output file path
            overwrite: Whether to overwrite existing file

        Returns:
            Command as list of strings
        """
        cmd = [self.ffmpeg_path]

        if overwrite:
            cmd.append("-y")

        cmd.extend(["-i", str(input_file), "-c", "copy", str(output_file)])  # Copy without re-encoding (fast)

        return cmd

    def get_video_info(self, video_file: Path) -> Optional[dict]:
        """
        Get video file information using ffprobe

        Args:
            video_file: Video file path

        Returns:
            Dict with video info or None if failed
        """
        try:
            cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(video_file)]

            result = subprocess.run(cmd, capture_output=True, check=True)
            import json

            return json.loads(result.stdout.decode("utf-8"))

        except Exception as e:
            self.logger.error(f"Error getting video info: {e}")
            return None
