"""
Tests for weekseries_downloader.download.media_converter module
"""

import subprocess
from unittest.mock import patch, MagicMock
from weekseries_downloader.download.media_converter import MediaConverter


class TestConvertToMp4:
    """Tests for convert_to_mp4 function"""

    @patch("weekseries_downloader.download.media_converter.subprocess.run")
    def test_convert_to_mp4_success(self, mock_run):
        """Test convert_to_mp4 with successful conversion"""
        # Mock successful subprocess run
        mock_run.return_value = MagicMock(returncode=0)

        converter = MediaConverter()
        result = converter.convert_to_mp4("input.ts", "output.mp4")

        assert result is True

        # Verify subprocess.run was called with correct arguments (ffmpeg -y -i input -c copy output)
        mock_run.assert_called_once_with(["ffmpeg", "-y", "-i", "input.ts", "-c", "copy", "output.mp4"], check=True, capture_output=True)

    @patch("weekseries_downloader.download.media_converter.subprocess.run")
    def test_convert_to_mp4_failure(self, mock_run):
        """Test convert_to_mp4 with failed conversion"""
        # Mock failed subprocess run
        mock_run.side_effect = subprocess.CalledProcessError(1, "ffmpeg")

        converter = MediaConverter()
        result = converter.convert_to_mp4("input.ts", "output.mp4")

        assert result is False

        # Verify subprocess.run was called
        mock_run.assert_called_once()

    @patch("weekseries_downloader.download.media_converter.subprocess.run")
    def test_convert_to_mp4_different_files(self, mock_run):
        """Test convert_to_mp4 with different input/output files"""
        mock_run.return_value = MagicMock(returncode=0)

        input_file = "episode_s01e01.ts"
        output_file = "episode_s01e01.mp4"

        converter = MediaConverter()
        result = converter.convert_to_mp4(input_file, output_file)

        assert result is True

        # Verify correct file paths were used (ffmpeg -y -i input -c copy output)
        expected_call = ["ffmpeg", "-y", "-i", input_file, "-c", "copy", output_file]
        mock_run.assert_called_once_with(expected_call, check=True, capture_output=True)

    @patch("weekseries_downloader.download.media_converter.subprocess.run")
    def test_convert_to_mp4_with_various_filenames(self, mock_run):
        """Test convert_to_mp4 with spaces and special characters in filenames"""
        mock_run.return_value = MagicMock(returncode=0)
        converter = MediaConverter()

        test_cases = [
            ("my video file.ts", "my video file.mp4"),
            ("series_title_episode.ts", "series_title_episode.mp4"),
            ("/path/to/input/video.ts", "/path/to/output/video.mp4"),
            ("./videos/input.ts", "../output/video.mp4"),
        ]

        for input_file, output_file in test_cases:
            mock_run.reset_mock()
            result = converter.convert_to_mp4(input_file, output_file)
            assert result is True
            expected_call = ["ffmpeg", "-y", "-i", input_file, "-c", "copy", output_file]
            mock_run.assert_called_once_with(expected_call, check=True, capture_output=True)


    @patch("weekseries_downloader.download.media_converter.subprocess.run")
    def test_convert_to_mp4_command_structure(self, mock_run):
        """Test convert_to_mp4 uses correct ffmpeg command structure"""
        mock_run.return_value = MagicMock(returncode=0)
        converter = MediaConverter()

        converter.convert_to_mp4("test.ts", "test.mp4")

        # Get the command that was called
        call_args = mock_run.call_args[0][0]

        # Verify command structure: ffmpeg -y -i input -c copy output
        assert call_args[0] == "ffmpeg"
        assert call_args[1] == "-y"
        assert call_args[2] == "-i"
        assert call_args[3] == "test.ts"
        assert call_args[4] == "-c"
        assert call_args[5] == "copy"
        assert call_args[6] == "test.mp4"

        # Verify subprocess options
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["check"] is True
        assert call_kwargs["capture_output"] is True

    @patch("weekseries_downloader.download.media_converter.subprocess.run")
    def test_convert_to_mp4_return_codes(self, mock_run):
        """Test convert_to_mp4 with different return codes"""
        # Test successful return code (0)
        mock_run.return_value = MagicMock(returncode=0)
        converter = MediaConverter()
        result = converter.convert_to_mp4("input.ts", "output.mp4")
        assert result is True

        # Test non-zero return code via CalledProcessError
        mock_run.side_effect = subprocess.CalledProcessError(2, "ffmpeg")
        converter = MediaConverter()
        result = converter.convert_to_mp4("input.ts", "output.mp4")
        assert result is False



class TestConverterIntegration:
    """Integration tests for converter module"""

    @patch("weekseries_downloader.download.media_converter.subprocess.run")
    def test_converter_workflow(self, mock_run):
        """Test complete converter workflow"""
        mock_run.return_value = MagicMock(returncode=0)

        # Simulate a typical conversion workflow
        input_files = ["episode1.ts", "episode2.ts", "episode3.ts"]
        output_files = ["episode1.mp4", "episode2.mp4", "episode3.mp4"]

        results = []
        for input_file, output_file in zip(input_files, output_files):
            converter = MediaConverter()
            result = converter.convert_to_mp4(input_file, output_file)
            results.append(result)

        # All conversions should succeed
        assert all(results)

        # Verify all files were processed
        assert mock_run.call_count == 3

    @patch("weekseries_downloader.download.media_converter.subprocess.run")
    def test_converter_mixed_results(self, mock_run):
        """Test converter with mixed success/failure results"""
        # First call succeeds, second fails, third succeeds
        mock_run.side_effect = [MagicMock(returncode=0), subprocess.CalledProcessError(1, "ffmpeg"), MagicMock(returncode=0)]

        files = [("file1.ts", "file1.mp4"), ("file2.ts", "file2.mp4"), ("file3.ts", "file3.mp4")]
        results = []

        for input_file, output_file in files:
            converter = MediaConverter()
            result = converter.convert_to_mp4(input_file, output_file)
            results.append(result)

        # Should have mixed results: True, False, True
        assert results == [True, False, True]
        assert mock_run.call_count == 3
