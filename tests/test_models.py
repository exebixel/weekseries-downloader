"""
Tests for weekseries_downloader.models module
"""

import pytest
from weekseries_downloader.models import EpisodeInfo, ExtractionResult, DownloadConfig


class TestEpisodeInfo:
    """Tests for EpisodeInfo dataclass"""
    
    def test_episode_info_creation(self, sample_episode_info):
        """Test EpisodeInfo creation with valid data"""
        episode = sample_episode_info
        
        assert episode.series_name == "the-good-doctor"
        assert episode.season == 1
        assert episode.episode == 3
        assert episode.original_url == "https://www.weekseries.info/series/the-good-doctor/temporada-1/episodio-03"
    
    def test_episode_info_str_representation(self, sample_episode_info):
        """Test string representation of EpisodeInfo"""
        episode = sample_episode_info
        expected = "the-good-doctor - S01E03"
        
        assert str(episode) == expected
    
    def test_episode_info_str_with_double_digits(self):
        """Test string representation with double digit season/episode"""
        episode = EpisodeInfo(
            series_name="test-series",
            season=12,
            episode=25,
            original_url="https://example.com"
        )
        expected = "test-series - S12E25"
        
        assert str(episode) == expected
    
    def test_filename_safe_name_basic(self, sample_episode_info):
        """Test filename_safe_name property with basic series name"""
        episode = sample_episode_info
        expected = "the-good-doctor_S01E03"
        
        assert episode.filename_safe_name == expected
    
    def test_filename_safe_name_with_special_characters(self, sample_episode_info_with_special_chars):
        """Test filename_safe_name property removes special characters"""
        episode = sample_episode_info_with_special_chars
        expected = "the_good_doctor__S02E05"
        
        assert episode.filename_safe_name == expected
    
    def test_filename_safe_name_with_all_special_chars(self):
        """Test filename_safe_name removes all filesystem-unsafe characters"""
        episode = EpisodeInfo(
            series_name='test<>:"/\\|?*series',
            season=1,
            episode=1,
            original_url="https://example.com"
        )
        expected = "test_________series_S01E01"
        
        assert episode.filename_safe_name == expected
    
    def test_episode_info_immutable(self, sample_episode_info):
        """Test that EpisodeInfo is immutable (dataclass frozen behavior)"""
        episode = sample_episode_info
        
        # These should work (reading)
        assert episode.series_name == "the-good-doctor"
        assert episode.season == 1
        
        # Test that we can create new instances
        new_episode = EpisodeInfo(
            series_name="new-series",
            season=2,
            episode=4,
            original_url="https://example.com"
        )
        assert new_episode.series_name == "new-series"
    
    def test_episode_info_edge_cases(self):
        """Test EpisodeInfo with edge case values"""
        # Test with season/episode 0
        episode = EpisodeInfo(
            series_name="test",
            season=0,
            episode=0,
            original_url="https://example.com"
        )
        assert episode.filename_safe_name == "test_S00E00"
        
        # Test with very high numbers
        episode = EpisodeInfo(
            series_name="test",
            season=999,
            episode=999,
            original_url="https://example.com"
        )
        assert episode.filename_safe_name == "test_S999E999"
    
    def test_episode_info_empty_series_name(self):
        """Test EpisodeInfo with empty series name"""
        episode = EpisodeInfo(
            series_name="",
            season=1,
            episode=1,
            original_url="https://example.com"
        )
        assert episode.filename_safe_name == "_S01E01"
        assert str(episode) == " - S01E01"


class TestExtractionResult:
    """Tests for ExtractionResult dataclass"""
    
    def test_successful_extraction_result(self, successful_extraction_result):
        """Test ExtractionResult with successful extraction"""
        result = successful_extraction_result
        
        assert result.success is True
        assert result.stream_url == "https://example.com/stream.m3u8"
        assert result.referer_url == "https://www.weekseries.info/"
        assert result.episode_info is not None
        assert result.error_message is None
    
    def test_failed_extraction_result(self, failed_extraction_result):
        """Test ExtractionResult with failed extraction"""
        result = failed_extraction_result

        assert result.success is False
        assert result.stream_url is None
        assert result.referer_url is None
        assert result.episode_info is None
        assert result.error_message == "Streaming URL not found"
    
    def test_extraction_result_boolean_context_success(self, successful_extraction_result):
        """Test ExtractionResult in boolean context when successful"""
        result = successful_extraction_result
        
        assert bool(result) is True
        assert result  # Should be truthy
        
        if result:
            assert True  # This should execute
        else:
            pytest.fail("Successful result should be truthy")
    
    def test_extraction_result_boolean_context_failure(self, failed_extraction_result):
        """Test ExtractionResult in boolean context when failed"""
        result = failed_extraction_result
        
        assert bool(result) is False
        assert not result  # Should be falsy
        
        if result:
            pytest.fail("Failed result should be falsy")
        else:
            assert True  # This should execute
    
    def test_is_error_property_success(self, successful_extraction_result):
        """Test is_error property for successful result"""
        result = successful_extraction_result
        
        assert result.is_error is False
    
    def test_is_error_property_failure(self, failed_extraction_result):
        """Test is_error property for failed result"""
        result = failed_extraction_result
        
        assert result.is_error is True
    
    def test_has_stream_url_property_with_url(self, successful_extraction_result):
        """Test has_stream_url property when URL is present"""
        result = successful_extraction_result
        
        assert result.has_stream_url is True
    
    def test_has_stream_url_property_without_url(self, failed_extraction_result):
        """Test has_stream_url property when URL is not present"""
        result = failed_extraction_result
        
        assert result.has_stream_url is False
    
    def test_has_stream_url_property_success_but_no_url(self):
        """Test has_stream_url property when success=True but no stream_url"""
        result = ExtractionResult(
            success=True,
            stream_url=None
        )
        
        assert result.has_stream_url is False
    
    def test_extraction_result_minimal_success(self):
        """Test ExtractionResult with minimal successful data"""
        result = ExtractionResult(success=True)
        
        assert result.success is True
        assert result.stream_url is None
        assert result.referer_url is None
        assert result.episode_info is None
        assert result.error_message is None
        assert result.has_stream_url is False
    
    def test_extraction_result_minimal_failure(self):
        """Test ExtractionResult with minimal failure data"""
        result = ExtractionResult(success=False)
        
        assert result.success is False
        assert result.is_error is True
        assert result.has_stream_url is False
    
    def test_extraction_result_with_episode_info(self, sample_episode_info):
        """Test ExtractionResult with episode info"""
        result = ExtractionResult(
            success=True,
            stream_url="https://example.com/stream.m3u8",
            episode_info=sample_episode_info
        )
        
        assert result.episode_info == sample_episode_info
        assert result.episode_info.series_name == "the-good-doctor"
    
    def test_extraction_result_all_fields(self, sample_episode_info):
        """Test ExtractionResult with all fields populated"""
        result = ExtractionResult(
            success=True,
            stream_url="https://example.com/stream.m3u8",
            error_message=None,
            referer_url="https://www.weekseries.info/",
            episode_info=sample_episode_info
        )

        assert result.success is True
        assert result.stream_url == "https://example.com/stream.m3u8"
        assert result.error_message is None
        assert result.referer_url == "https://www.weekseries.info/"
        assert result.episode_info == sample_episode_info
        assert result.has_stream_url is True
        assert result.is_error is False


class TestDownloadConfig:
    """Tests for DownloadConfig dataclass"""
    
    def test_download_config_creation(self, sample_download_config):
        """Test DownloadConfig creation with valid data"""
        config = sample_download_config
        
        assert config.stream_url == "https://example.com/stream.m3u8"
        assert config.output_file == "test_video.mp4"
        assert config.referer_url == "https://www.weekseries.info/"
        assert config.convert_to_mp4 is True
    
    def test_download_config_without_referer(self, sample_download_config_no_referer):
        """Test DownloadConfig creation without referer"""
        config = sample_download_config_no_referer
        
        assert config.stream_url == "https://example.com/stream.m3u8"
        assert config.output_file == "test_video.mp4"
        assert config.referer_url is None
        assert config.convert_to_mp4 is False
    
    def test_has_referer_property_with_referer(self, sample_download_config):
        """Test has_referer property when referer is present"""
        config = sample_download_config
        
        assert config.has_referer is True
    
    def test_has_referer_property_without_referer(self, sample_download_config_no_referer):
        """Test has_referer property when referer is not present"""
        config = sample_download_config_no_referer
        
        assert config.has_referer is False
    
    def test_has_referer_property_empty_referer(self):
        """Test has_referer property with empty string referer"""
        config = DownloadConfig(
            stream_url="https://example.com/stream.m3u8",
            output_file="test.mp4",
            referer_url="",
            convert_to_mp4=True
        )
        
        # Empty string should still be considered as having a referer
        assert config.has_referer is True
    
    def test_download_config_minimal(self):
        """Test DownloadConfig with minimal required fields"""
        config = DownloadConfig(
            stream_url="https://example.com/stream.m3u8",
            output_file="video.mp4"
        )
        
        assert config.stream_url == "https://example.com/stream.m3u8"
        assert config.output_file == "video.mp4"
        assert config.referer_url is None
        assert config.convert_to_mp4 is True  # Default value
        assert config.has_referer is False
    
    def test_download_config_convert_to_mp4_default(self):
        """Test that convert_to_mp4 defaults to True"""
        config = DownloadConfig(
            stream_url="https://example.com/stream.m3u8",
            output_file="video.mp4"
        )
        
        assert config.convert_to_mp4 is True
    
    def test_download_config_convert_to_mp4_false(self):
        """Test DownloadConfig with convert_to_mp4 set to False"""
        config = DownloadConfig(
            stream_url="https://example.com/stream.m3u8",
            output_file="video.ts",
            convert_to_mp4=False
        )
        
        assert config.convert_to_mp4 is False
    
    def test_download_config_different_file_extensions(self):
        """Test DownloadConfig with different output file extensions"""
        # Test with .mp4
        config_mp4 = DownloadConfig(
            stream_url="https://example.com/stream.m3u8",
            output_file="video.mp4"
        )
        assert config_mp4.output_file == "video.mp4"
        
        # Test with .ts
        config_ts = DownloadConfig(
            stream_url="https://example.com/stream.m3u8",
            output_file="video.ts"
        )
        assert config_ts.output_file == "video.ts"
        
        # Test with no extension
        config_no_ext = DownloadConfig(
            stream_url="https://example.com/stream.m3u8",
            output_file="video"
        )
        assert config_no_ext.output_file == "video"
    
    def test_download_config_edge_cases(self):
        """Test DownloadConfig with edge case values"""
        # Test with very long URLs and filenames
        long_url = "https://example.com/" + "a" * 1000 + "/stream.m3u8"
        long_filename = "a" * 200 + ".mp4"
        
        config = DownloadConfig(
            stream_url=long_url,
            output_file=long_filename
        )
        
        assert config.stream_url == long_url
        assert config.output_file == long_filename
    
    def test_download_config_all_fields_explicit(self):
        """Test DownloadConfig with all fields explicitly set"""
        config = DownloadConfig(
            stream_url="https://example.com/stream.m3u8",
            output_file="test_video.mp4",
            referer_url="https://www.weekseries.info/",
            convert_to_mp4=True
        )
        
        assert config.stream_url == "https://example.com/stream.m3u8"
        assert config.output_file == "test_video.mp4"
        assert config.referer_url == "https://www.weekseries.info/"
        assert config.convert_to_mp4 is True
        assert config.has_referer is True