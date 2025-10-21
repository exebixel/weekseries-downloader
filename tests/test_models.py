"""
Tests for weekseries_downloader.models module
"""

import pytest
from weekseries_downloader.models import EpisodeInfo, ExtractionResult


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

    def test_extraction_result_minimal_success(self):
        """Test ExtractionResult with minimal successful data"""
        result = ExtractionResult(success=True)
        
        assert result.success is True
        assert result.stream_url is None
        assert result.referer_url is None
        assert result.episode_info is None
        assert result.error_message is None

    def test_extraction_result_minimal_failure(self):
        """Test ExtractionResult with minimal failure data"""
        result = ExtractionResult(success=False)

        assert result.success is False
    
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