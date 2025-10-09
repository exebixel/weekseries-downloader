"""
Tests for weekseries_downloader.converter module
"""

import pytest
import subprocess
from unittest.mock import patch, MagicMock
from weekseries_downloader.converter import convert_to_mp4


class TestConvertToMp4:
    """Tests for convert_to_mp4 function"""
    
    @patch('weekseries_downloader.converter.subprocess.run')
    def test_convert_to_mp4_success(self, mock_run):
        """Test convert_to_mp4 with successful conversion"""
        # Mock successful subprocess run
        mock_run.return_value = MagicMock(returncode=0)
        
        result = convert_to_mp4("input.ts", "output.mp4")
        
        assert result is True
        
        # Verify subprocess.run was called with correct arguments
        mock_run.assert_called_once_with([
            "ffmpeg",
            "-i",
            "input.ts",
            "-c",
            "copy",
            "-y",
            "output.mp4"
        ], check=True, capture_output=True)
    
    @patch('weekseries_downloader.converter.subprocess.run')
    def test_convert_to_mp4_failure(self, mock_run):
        """Test convert_to_mp4 with failed conversion"""
        # Mock failed subprocess run
        mock_run.side_effect = subprocess.CalledProcessError(1, 'ffmpeg')
        
        result = convert_to_mp4("input.ts", "output.mp4")
        
        assert result is False
        
        # Verify subprocess.run was called
        mock_run.assert_called_once()
    
    @patch('weekseries_downloader.converter.subprocess.run')
    def test_convert_to_mp4_different_files(self, mock_run):
        """Test convert_to_mp4 with different input/output files"""
        mock_run.return_value = MagicMock(returncode=0)
        
        input_file = "episode_s01e01.ts"
        output_file = "episode_s01e01.mp4"
        
        result = convert_to_mp4(input_file, output_file)
        
        assert result is True
        
        # Verify correct file paths were used
        expected_call = [
            "ffmpeg",
            "-i",
            input_file,
            "-c",
            "copy",
            "-y",
            output_file
        ]
        mock_run.assert_called_once_with(expected_call, check=True, capture_output=True)
    
    @patch('weekseries_downloader.converter.subprocess.run')
    def test_convert_to_mp4_with_spaces_in_filename(self, mock_run):
        """Test convert_to_mp4 with spaces in filenames"""
        mock_run.return_value = MagicMock(returncode=0)
        
        input_file = "my video file.ts"
        output_file = "my video file.mp4"
        
        result = convert_to_mp4(input_file, output_file)
        
        assert result is True
        
        # Verify filenames with spaces are handled correctly
        expected_call = [
            "ffmpeg",
            "-i",
            input_file,
            "-c",
            "copy",
            "-y",
            output_file
        ]
        mock_run.assert_called_once_with(expected_call, check=True, capture_output=True)
    
    @patch('weekseries_downloader.converter.subprocess.run')
    def test_convert_to_mp4_with_special_characters(self, mock_run):
        """Test convert_to_mp4 with special characters in filenames"""
        mock_run.return_value = MagicMock(returncode=0)
        
        input_file = "série_título_episódio.ts"
        output_file = "série_título_episódio.mp4"
        
        result = convert_to_mp4(input_file, output_file)
        
        assert result is True
        
        # Verify special characters are handled correctly
        expected_call = [
            "ffmpeg",
            "-i",
            input_file,
            "-c",
            "copy",
            "-y",
            output_file
        ]
        mock_run.assert_called_once_with(expected_call, check=True, capture_output=True)
    
    @patch('weekseries_downloader.converter.subprocess.run')
    def test_convert_to_mp4_ffmpeg_not_found(self, mock_run):
        """Test convert_to_mp4 when ffmpeg is not found"""
        mock_run.side_effect = FileNotFoundError("ffmpeg not found")
        
        # FileNotFoundError is not caught by convert_to_mp4, so it should raise
        with pytest.raises(FileNotFoundError):
            convert_to_mp4("input.ts", "output.mp4")
        
        mock_run.assert_called_once()
    
    @patch('weekseries_downloader.converter.subprocess.run')
    def test_convert_to_mp4_permission_error(self, mock_run):
        """Test convert_to_mp4 with permission error"""
        mock_run.side_effect = PermissionError("Permission denied")
        
        # PermissionError is not caught by convert_to_mp4, so it should raise
        with pytest.raises(PermissionError):
            convert_to_mp4("input.ts", "output.mp4")
        
        mock_run.assert_called_once()
    
    @patch('weekseries_downloader.converter.subprocess.run')
    def test_convert_to_mp4_other_exception(self, mock_run):
        """Test convert_to_mp4 with other unexpected exception"""
        mock_run.side_effect = OSError("Unexpected error")
        
        # OSError is not caught by convert_to_mp4, so it should raise
        with pytest.raises(OSError):
            convert_to_mp4("input.ts", "output.mp4")
        
        mock_run.assert_called_once()
    
    @patch('weekseries_downloader.converter.subprocess.run')
    def test_convert_to_mp4_command_structure(self, mock_run):
        """Test convert_to_mp4 uses correct ffmpeg command structure"""
        mock_run.return_value = MagicMock(returncode=0)
        
        convert_to_mp4("test.ts", "test.mp4")
        
        # Get the command that was called
        call_args = mock_run.call_args[0][0]
        
        # Verify command structure
        assert call_args[0] == "ffmpeg"
        assert call_args[1] == "-i"
        assert call_args[2] == "test.ts"
        assert call_args[3] == "-c"
        assert call_args[4] == "copy"
        assert call_args[5] == "-y"
        assert call_args[6] == "test.mp4"
        
        # Verify subprocess options
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs['check'] is True
        assert call_kwargs['capture_output'] is True
    
    @patch('weekseries_downloader.converter.subprocess.run')
    def test_convert_to_mp4_empty_filenames(self, mock_run):
        """Test convert_to_mp4 with empty filenames"""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = convert_to_mp4("", "")
        
        assert result is True
        
        # Should still call ffmpeg even with empty strings
        expected_call = [
            "ffmpeg",
            "-i",
            "",
            "-c",
            "copy",
            "-y",
            ""
        ]
        mock_run.assert_called_once_with(expected_call, check=True, capture_output=True)
    
    @patch('weekseries_downloader.converter.subprocess.run')
    def test_convert_to_mp4_path_with_directories(self, mock_run):
        """Test convert_to_mp4 with file paths including directories"""
        mock_run.return_value = MagicMock(returncode=0)
        
        input_file = "/path/to/input/video.ts"
        output_file = "/path/to/output/video.mp4"
        
        result = convert_to_mp4(input_file, output_file)
        
        assert result is True
        
        expected_call = [
            "ffmpeg",
            "-i",
            input_file,
            "-c",
            "copy",
            "-y",
            output_file
        ]
        mock_run.assert_called_once_with(expected_call, check=True, capture_output=True)
    
    @patch('weekseries_downloader.converter.subprocess.run')
    def test_convert_to_mp4_relative_paths(self, mock_run):
        """Test convert_to_mp4 with relative file paths"""
        mock_run.return_value = MagicMock(returncode=0)
        
        input_file = "./videos/input.ts"
        output_file = "../output/video.mp4"
        
        result = convert_to_mp4(input_file, output_file)
        
        assert result is True
        
        expected_call = [
            "ffmpeg",
            "-i",
            input_file,
            "-c",
            "copy",
            "-y",
            output_file
        ]
        mock_run.assert_called_once_with(expected_call, check=True, capture_output=True)
    
    @patch('weekseries_downloader.converter.subprocess.run')
    def test_convert_to_mp4_return_codes(self, mock_run):
        """Test convert_to_mp4 with different return codes"""
        # Test successful return code (0)
        mock_run.return_value = MagicMock(returncode=0)
        result = convert_to_mp4("input.ts", "output.mp4")
        assert result is True
        
        # Test non-zero return code via CalledProcessError
        mock_run.side_effect = subprocess.CalledProcessError(2, 'ffmpeg')
        result = convert_to_mp4("input.ts", "output.mp4")
        assert result is False
    
    @patch('weekseries_downloader.converter.logger')
    @patch('weekseries_downloader.converter.subprocess.run')
    def test_convert_to_mp4_logging(self, mock_run, mock_logger):
        """Test convert_to_mp4 logging behavior"""
        mock_run.return_value = MagicMock(returncode=0)
        
        convert_to_mp4("input.ts", "output.mp4")
        
        # Verify info logging for start and completion
        mock_logger.info.assert_any_call("Convertendo para MP4...")
        mock_logger.info.assert_any_call("Conversão completa! Arquivo MP4: output.mp4")
    
    @patch('weekseries_downloader.converter.logger')
    @patch('weekseries_downloader.converter.subprocess.run')
    def test_convert_to_mp4_error_logging(self, mock_run, mock_logger):
        """Test convert_to_mp4 error logging"""
        error = subprocess.CalledProcessError(1, 'ffmpeg')
        mock_run.side_effect = error
        
        convert_to_mp4("input.ts", "output.mp4")
        
        # Verify error logging
        mock_logger.error.assert_called_once_with(f"Erro ao converter: {error}")


class TestConverterIntegration:
    """Integration tests for converter module"""
    
    @patch('weekseries_downloader.converter.subprocess.run')
    def test_converter_workflow(self, mock_run):
        """Test complete converter workflow"""
        mock_run.return_value = MagicMock(returncode=0)
        
        # Simulate a typical conversion workflow
        input_files = ["episode1.ts", "episode2.ts", "episode3.ts"]
        output_files = ["episode1.mp4", "episode2.mp4", "episode3.mp4"]
        
        results = []
        for input_file, output_file in zip(input_files, output_files):
            result = convert_to_mp4(input_file, output_file)
            results.append(result)
        
        # All conversions should succeed
        assert all(results)
        
        # Verify all files were processed
        assert mock_run.call_count == 3
    
    @patch('weekseries_downloader.converter.subprocess.run')
    def test_converter_mixed_results(self, mock_run):
        """Test converter with mixed success/failure results"""
        # First call succeeds, second fails, third succeeds
        mock_run.side_effect = [
            MagicMock(returncode=0),
            subprocess.CalledProcessError(1, 'ffmpeg'),
            MagicMock(returncode=0)
        ]
        
        files = [("file1.ts", "file1.mp4"), ("file2.ts", "file2.mp4"), ("file3.ts", "file3.mp4")]
        results = []
        
        for input_file, output_file in files:
            result = convert_to_mp4(input_file, output_file)
            results.append(result)
        
        # Should have mixed results: True, False, True
        assert results == [True, False, True]
        assert mock_run.call_count == 3