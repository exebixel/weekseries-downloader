"""
Series page parser for extracting episode links
"""

import re
import logging
from typing import Optional, List, Dict
from urllib.parse import urljoin

from ..models import EpisodeLink, SeriesInfo
from ..exceptions import SeriesParsingError, NetworkError
from ..infrastructure.http_client import HTTPClient
from ..infrastructure.parsers import HTMLParser

logger = logging.getLogger(__name__)


class SeriesParser:
    """Parses series pages to extract episode information"""

    # Regex to find episode links in the HTML
    EPISODE_LINK_PATTERN = re.compile(r'href="(/series/[^"]+/temporada-(\d+)/episodio-(\d+))"')

    def __init__(self, http_client: Optional[HTTPClient] = None, html_parser: Optional[HTMLParser] = None):
        """
        Initialize SeriesParser with dependencies

        Args:
            http_client: HTTP client for fetching pages (optional)
            html_parser: HTML parser instance (optional)
        """
        self.http_client = http_client or HTTPClient()
        self.html_parser = html_parser or HTMLParser()

    @classmethod
    def create_default(cls) -> "SeriesParser":
        """Factory method with default dependencies"""
        return cls()

    def parse_series_page(self, series_url: str) -> SeriesInfo:
        """
        Parse series page and extract all episode links

        Steps:
        1. Fetch series page HTML
        2. Find all episode links matching pattern
        3. Extract season/episode numbers from URLs
        4. Group episodes by season
        5. Return SeriesInfo with organized data

        Args:
            series_url: URL of the series page

        Returns:
            SeriesInfo with all episodes organized by season

        Raises:
            NetworkError: If page cannot be fetched
            SeriesParsingError: If parsing fails or no episodes found
        """
        logger.info(f"Parsing series page: {series_url}")

        # Fetch series page HTML
        try:
            html_content = self.http_client.fetch(series_url)
        except Exception as e:
            logger.error(f"Failed to fetch series page: {series_url}")
            raise NetworkError(series_url, e)

        if not html_content:
            raise SeriesParsingError(series_url, "Empty response from server")

        # Extract episode links
        episode_links = self._extract_episode_links(html_content, series_url)

        if not episode_links:
            raise SeriesParsingError(series_url, "No episodes found on page")

        # Organize by season
        seasons = self._organize_by_season(episode_links)

        # Extract series name from URL
        series_name = self._extract_series_name_from_url(series_url)

        # Create SeriesInfo
        series_info = SeriesInfo(series_name=series_name, series_url=series_url, total_episodes=len(episode_links), seasons=seasons)

        logger.info(f"Found {len(episode_links)} episodes across {len(seasons)} seasons for {series_name}")
        return series_info

    def _extract_episode_links(self, html: str, base_url: str) -> List[EpisodeLink]:
        """
        Extract episode links from HTML using regex

        Args:
            html: HTML content of series page
            base_url: Base URL for constructing absolute URLs

        Returns:
            List of EpisodeLink objects
        """
        episode_links = []
        seen_urls = set()  # To avoid duplicates

        # Find all matches in the HTML
        matches = self.EPISODE_LINK_PATTERN.findall(html)

        for match in matches:
            url, season_str, episode_str = match
            season = int(season_str)
            episode = int(episode_str)

            # Skip duplicates
            if url in seen_urls:
                continue
            seen_urls.add(url)

            # Construct full URL
            full_url = urljoin(base_url, url)

            episode_link = EpisodeLink(url=url, season=season, episode=episode, full_url=full_url)
            episode_links.append(episode_link)

        # Sort by season and episode
        episode_links.sort(key=lambda x: (x.season, x.episode))

        return episode_links

    def _organize_by_season(self, episodes: List[EpisodeLink]) -> Dict[int, List[EpisodeLink]]:
        """
        Group episodes by season number

        Args:
            episodes: List of EpisodeLink objects

        Returns:
            Dictionary mapping season number to list of episodes
        """
        seasons: Dict[int, List[EpisodeLink]] = {}

        for episode in episodes:
            if episode.season not in seasons:
                seasons[episode.season] = []
            seasons[episode.season].append(episode)

        # Sort episodes within each season
        for season_episodes in seasons.values():
            season_episodes.sort(key=lambda x: x.episode)

        return seasons

    def _extract_series_name_from_url(self, series_url: str) -> str:
        """
        Extract series name from series URL

        Args:
            series_url: URL of the series page

        Returns:
            Series name extracted from URL
        """
        # Pattern: https://www.weekseries.info/series/{series-name}
        match = re.search(r"/series/([^/]+)", series_url)
        if match:
            return match.group(1)

        # Fallback: use the last part of the URL
        return series_url.rstrip("/").split("/")[-1]
