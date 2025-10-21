"""
Tests for series_processing.series_parser module
"""

import pytest
from unittest.mock import Mock
from weekseries_downloader.series_processing import SeriesParser
from weekseries_downloader.models import EpisodeLink, SeriesInfo
from weekseries_downloader.exceptions import SeriesParsingError, NetworkError


class TestSeriesParser:
    """Tests for SeriesParser class"""

    @pytest.fixture
    def mock_http_client(self):
        """Create mock HTTP client"""
        mock = Mock()
        return mock

    @pytest.fixture
    def series_parser(self, mock_http_client):
        """Create SeriesParser with mock dependencies"""
        return SeriesParser(http_client=mock_http_client)

    @pytest.fixture
    def simple_series_html(self):
        """HTML with 3 episodes from 1 season"""
        return """
        <html>
            <body>
                <div class="episodes">
                    <a href="/series/test-series/temporada-1/episodio-01">Episode 1</a>
                    <a href="/series/test-series/temporada-1/episodio-02">Episode 2</a>
                    <a href="/series/test-series/temporada-1/episodio-03">Episode 3</a>
                </div>
            </body>
        </html>
        """

    @pytest.fixture
    def multi_season_html(self):
        """HTML with episodes from multiple seasons"""
        return """
        <html>
            <body>
                <div class="episodes">
                    <h2>1° Temporada</h2>
                    <a href="/series/breaking-bad/temporada-1/episodio-01">S01E01</a>
                    <a href="/series/breaking-bad/temporada-1/episodio-02">S01E02</a>
                    <h2>2° Temporada</h2>
                    <a href="/series/breaking-bad/temporada-2/episodio-01">S02E01</a>
                    <a href="/series/breaking-bad/temporada-2/episodio-02">S02E02</a>
                    <a href="/series/breaking-bad/temporada-2/episodio-03">S02E03</a>
                </div>
            </body>
        </html>
        """

    def test_create_default(self):
        """Test factory method creates parser with default dependencies"""
        parser = SeriesParser.create_default()
        assert parser is not None
        assert parser.http_client is not None
        assert parser.html_parser is not None

    def test_parse_series_page_simple(self, series_parser, mock_http_client, simple_series_html):
        """Test parsing simple series page with one season"""
        series_url = "https://www.weekseries.info/series/test-series"
        mock_http_client.fetch.return_value = simple_series_html

        result = series_parser.parse_series_page(series_url)

        assert isinstance(result, SeriesInfo)
        assert result.series_name == "test-series"
        assert result.series_url == series_url
        assert result.total_episodes == 3
        assert len(result.seasons) == 1
        assert 1 in result.seasons
        assert len(result.seasons[1]) == 3

    def test_parse_series_page_multi_season(self, series_parser, mock_http_client, multi_season_html):
        """Test parsing series page with multiple seasons"""
        series_url = "https://www.weekseries.info/series/breaking-bad"
        mock_http_client.fetch.return_value = multi_season_html

        result = series_parser.parse_series_page(series_url)

        assert isinstance(result, SeriesInfo)
        assert result.series_name == "breaking-bad"
        assert result.total_episodes == 5
        assert len(result.seasons) == 2
        assert 1 in result.seasons
        assert 2 in result.seasons
        assert len(result.seasons[1]) == 2
        assert len(result.seasons[2]) == 3

    def test_parse_series_page_episode_links_structure(self, series_parser, mock_http_client, simple_series_html):
        """Test that episode links have correct structure"""
        series_url = "https://www.weekseries.info/series/test-series"
        mock_http_client.fetch.return_value = simple_series_html

        result = series_parser.parse_series_page(series_url)
        episode = result.seasons[1][0]

        assert isinstance(episode, EpisodeLink)
        assert episode.url == "/series/test-series/temporada-1/episodio-01"
        assert episode.season == 1
        assert episode.episode == 1
        assert episode.full_url == "https://www.weekseries.info/series/test-series/temporada-1/episodio-01"

    def test_parse_series_page_sorts_episodes(self, series_parser, mock_http_client):
        """Test that episodes are sorted by season and episode number"""
        html = """
        <a href="/series/test/temporada-2/episodio-03">S02E03</a>
        <a href="/series/test/temporada-1/episodio-02">S01E02</a>
        <a href="/series/test/temporada-2/episodio-01">S02E01</a>
        <a href="/series/test/temporada-1/episodio-01">S01E01</a>
        """
        series_url = "https://www.weekseries.info/series/test"
        mock_http_client.fetch.return_value = html

        result = series_parser.parse_series_page(series_url)

        # Check season 1 is sorted
        assert result.seasons[1][0].episode == 1
        assert result.seasons[1][1].episode == 2

        # Check season 2 is sorted
        assert result.seasons[2][0].episode == 1
        assert result.seasons[2][1].episode == 3

    def test_parse_series_page_removes_duplicates(self, series_parser, mock_http_client):
        """Test that duplicate episode links are removed"""
        html = """
        <a href="/series/test/temporada-1/episodio-01">Episode 1</a>
        <a href="/series/test/temporada-1/episodio-01">Episode 1 (duplicate)</a>
        <a href="/series/test/temporada-1/episodio-02">Episode 2</a>
        """
        series_url = "https://www.weekseries.info/series/test"
        mock_http_client.fetch.return_value = html

        result = series_parser.parse_series_page(series_url)

        assert result.total_episodes == 2
        assert len(result.seasons[1]) == 2

    def test_parse_series_page_empty_response(self, series_parser, mock_http_client):
        """Test error handling for empty response"""
        series_url = "https://www.weekseries.info/series/test"
        mock_http_client.fetch.return_value = ""

        with pytest.raises(SeriesParsingError) as exc_info:
            series_parser.parse_series_page(series_url)

        assert "Empty response" in str(exc_info.value)

    def test_parse_series_page_no_episodes_found(self, series_parser, mock_http_client):
        """Test error handling when no episodes are found"""
        html = "<html><body><h1>Series Page</h1></body></html>"
        series_url = "https://www.weekseries.info/series/test"
        mock_http_client.fetch.return_value = html

        with pytest.raises(SeriesParsingError) as exc_info:
            series_parser.parse_series_page(series_url)

        assert "No episodes found" in str(exc_info.value)

    def test_parse_series_page_network_error(self, series_parser, mock_http_client):
        """Test error handling for network errors"""
        series_url = "https://www.weekseries.info/series/test"
        mock_http_client.fetch.side_effect = Exception("Connection failed")

        with pytest.raises(NetworkError) as exc_info:
            series_parser.parse_series_page(series_url)

        assert "Connection failed" in str(exc_info.value)

    def test_extract_series_name_from_url(self, series_parser):
        """Test series name extraction from URL"""
        test_cases = [
            ("https://www.weekseries.info/series/the-good-doctor", "the-good-doctor"),
            ("https://www.weekseries.info/series/breaking-bad/", "breaking-bad"),
            ("http://weekseries.info/series/game-of-thrones", "game-of-thrones"),
        ]

        for url, expected_name in test_cases:
            result = series_parser._extract_series_name_from_url(url)
            assert result == expected_name

    def test_get_episodes_all_seasons(self, series_parser, mock_http_client, multi_season_html):
        """Test getting all episodes from SeriesInfo"""
        series_url = "https://www.weekseries.info/series/test"
        mock_http_client.fetch.return_value = multi_season_html

        result = series_parser.parse_series_page(series_url)
        all_episodes = result.get_episodes()

        assert len(all_episodes) == 5
        # Should be sorted by season then episode
        assert all_episodes[0].season == 1
        assert all_episodes[0].episode == 1
        assert all_episodes[-1].season == 2
        assert all_episodes[-1].episode == 3

    def test_get_episodes_single_season(self, series_parser, mock_http_client, multi_season_html):
        """Test getting episodes from specific season"""
        series_url = "https://www.weekseries.info/series/test"
        mock_http_client.fetch.return_value = multi_season_html

        result = series_parser.parse_series_page(series_url)
        season_1_episodes = result.get_episodes(season_filter=1)
        season_2_episodes = result.get_episodes(season_filter=2)

        assert len(season_1_episodes) == 2
        assert all(ep.season == 1 for ep in season_1_episodes)

        assert len(season_2_episodes) == 3
        assert all(ep.season == 2 for ep in season_2_episodes)

    def test_get_episodes_nonexistent_season(self, series_parser, mock_http_client, multi_season_html):
        """Test getting episodes from nonexistent season returns empty list"""
        series_url = "https://www.weekseries.info/series/test"
        mock_http_client.fetch.return_value = multi_season_html

        result = series_parser.parse_series_page(series_url)
        episodes = result.get_episodes(season_filter=99)

        assert len(episodes) == 0

    def test_series_info_str_representation(self, series_parser, mock_http_client, multi_season_html):
        """Test string representation of SeriesInfo"""
        series_url = "https://www.weekseries.info/series/breaking-bad"
        mock_http_client.fetch.return_value = multi_season_html

        result = series_parser.parse_series_page(series_url)
        str_repr = str(result)

        assert "breaking-bad" in str_repr
        assert "2 seasons" in str_repr
        assert "5 episodes" in str_repr

    def test_episode_link_str_representation(self):
        """Test string representation of EpisodeLink"""
        episode = EpisodeLink(
            url="/series/test/temporada-1/episodio-01",
            season=1,
            episode=1,
            full_url="https://www.weekseries.info/series/test/temporada-1/episodio-01",
        )

        str_repr = str(episode)
        assert str_repr == "S01E01"

    def test_parse_large_series(self, series_parser, mock_http_client):
        """Test parsing a series with many episodes"""
        # Generate HTML with 50 episodes across 5 seasons
        episodes_html = []
        for season in range(1, 6):
            for episode in range(1, 11):
                episodes_html.append(f'<a href="/series/large-series/temporada-{season}/episodio-{episode:02d}">S{season:02d}E{episode:02d}</a>')

        html = "<html><body>" + "".join(episodes_html) + "</body></html>"
        series_url = "https://www.weekseries.info/series/large-series"
        mock_http_client.fetch.return_value = html

        result = series_parser.parse_series_page(series_url)

        assert result.total_episodes == 50
        assert len(result.seasons) == 5
        for season_num in range(1, 6):
            assert len(result.seasons[season_num]) == 10
