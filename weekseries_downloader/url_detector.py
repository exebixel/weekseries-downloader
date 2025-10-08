"""
Módulo para detecção e validação de URLs usando funções puras
"""

import re
from enum import Enum
from typing import Optional


class UrlType(Enum):
    """Tipos de URL suportados"""
    WEEKSERIES = "weekseries"
    DIRECT_STREAM = "direct_stream"
    BASE64 = "base64"
    UNKNOWN = "unknown"


# Padrão regex para URLs do weekseries.info
WEEKSERIES_PATTERN = re.compile(
    r'https?://(?:www\.)?weekseries\.info/series/([^/]+)/temporada-(\d+)/episodio-(\d+)'
)


def detect_url_type(url: str) -> UrlType:
    """
    Detecta tipo de URL usando early returns
    
    Args:
        url: URL a ser analisada
        
    Returns:
        UrlType correspondente ao tipo detectado
    """
    if not url:
        return UrlType.UNKNOWN
    
    if validate_weekseries_url(url):
        return UrlType.WEEKSERIES
    
    if is_stream_url(url):
        return UrlType.DIRECT_STREAM
    
    if is_base64_string(url):
        return UrlType.BASE64
    
    return UrlType.UNKNOWN


def validate_weekseries_url(url: str) -> bool:
    """
    Valida se URL é do weekseries.info usando early return
    
    Args:
        url: URL a ser validada
        
    Returns:
        True se for URL válida do weekseries.info
    """
    if not url:
        return False
    
    if not url.startswith(('http://', 'https://')):
        return False
    
    if 'weekseries.info' not in url:
        return False
    
    return WEEKSERIES_PATTERN.match(url) is not None


def is_stream_url(url: str) -> bool:
    """
    Verifica se é URL direta de streaming usando early return
    
    Args:
        url: URL a ser verificada
        
    Returns:
        True se for URL de streaming direto
    """
    if not url:
        return False
    
    if not url.startswith(('http://', 'https://')):
        return False
    
    return url.endswith('.m3u8') or 'stream' in url.lower()


def is_base64_string(text: str) -> bool:
    """
    Verifica se string é base64 válida usando early return
    
    Args:
        text: String a ser verificada
        
    Returns:
        True se for string base64 válida
    """
    if not text:
        return False
    
    if len(text) < 4:
        return False
    
    if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', text):
        return False
    
    return True


def extract_episode_info(url: str) -> Optional[dict]:
    """
    Extrai informações do episódio da URL do weekseries
    
    Args:
        url: URL do weekseries.info
        
    Returns:
        Dict com informações extraídas ou None se inválida
    """
    if not validate_weekseries_url(url):
        return None
    
    match = WEEKSERIES_PATTERN.match(url)
    if not match:
        return None
    
    series_name, season, episode = match.groups()
    
    return {
        'series_name': series_name,
        'season': int(season),
        'episode': int(episode),
        'original_url': url
    }