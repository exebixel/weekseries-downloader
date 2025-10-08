"""
Classes de dados para o weekseries downloader
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class EpisodeInfo:
    """Informações extraídas da URL do episódio"""
    series_name: str
    season: int
    episode: int
    original_url: str
    
    def __str__(self) -> str:
        """Representação string amigável"""
        return f"{self.series_name} - S{self.season:02d}E{self.episode:02d}"
    
    @property
    def filename_safe_name(self) -> str:
        """Nome seguro para usar em arquivos"""
        import re
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', self.series_name)
        return f"{safe_name}_S{self.season:02d}E{self.episode:02d}"


@dataclass
class ExtractionResult:
    """Resultado da extração de URL de streaming"""
    success: bool
    stream_url: Optional[str] = None
    error_message: Optional[str] = None
    referer_url: Optional[str] = None
    episode_info: Optional[EpisodeInfo] = None
    
    def __bool__(self) -> bool:
        """Permite usar em contextos booleanos"""
        return self.success
    
    @property
    def is_error(self) -> bool:
        """Verifica se houve erro"""
        return not self.success
    
    @property
    def has_stream_url(self) -> bool:
        """Verifica se tem URL de streaming"""
        return self.success and self.stream_url is not None


@dataclass
class DownloadConfig:
    """Configuração para download"""
    stream_url: str
    output_file: str
    referer_url: Optional[str] = None
    convert_to_mp4: bool = True
    
    @property
    def has_referer(self) -> bool:
        """Verifica se tem referer configurado"""
        return self.referer_url is not None