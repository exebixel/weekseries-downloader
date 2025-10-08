"""
Módulo para extração de URLs de streaming do weekseries.info usando padrão funcional
"""

import re
import urllib.request
import urllib.error
from typing import Protocol, Optional, Callable
from dataclasses import dataclass

from weekseries_downloader.url_detector import validate_weekseries_url, extract_episode_info
from weekseries_downloader.utils import decode_base64_url
from weekseries_downloader.models import ExtractionResult, EpisodeInfo
from weekseries_downloader.cache import get_cached_stream_url, cache_stream_url
from weekseries_downloader.logging_config import get_logger

logger = get_logger(__name__)


# Dependency Injection Protocols
class HttpClient(Protocol):
    """Protocolo para cliente HTTP"""
    def fetch(self, url: str, headers: dict) -> Optional[str]:
        """Faz requisição HTTP e retorna conteúdo"""
        ...


class HtmlParser(Protocol):
    """Protocolo para parser HTML"""
    def parse_stream_url(self, content: str) -> Optional[str]:
        """Parseia HTML/JS para encontrar URL de streaming"""
        ...


class Base64Decoder(Protocol):
    """Protocolo para decodificador base64"""
    def decode(self, encoded: str) -> Optional[str]:
        """Decodifica string base64"""
        ...


# ExtractionResult agora importado de models.py


def extract_stream_url(
    page_url: str,
    http_client: HttpClient,
    html_parser: HtmlParser,
    base64_decoder: Base64Decoder,
    url_validator: Callable[[str], bool],
    use_cache: bool = True
) -> ExtractionResult:
    """
    Extrai URL de streaming usando injeção de dependências
    
    Args:
        page_url: URL da página do weekseries.info
        http_client: Cliente HTTP para requisições
        html_parser: Parser para extrair URL do HTML
        base64_decoder: Decodificador base64
        url_validator: Função de validação de URL
        use_cache: Se deve usar cache para URLs já extraídas
        
    Returns:
        ExtractionResult com resultado da extração
    """
    # Early return para URL inválida
    if not url_validator(page_url):
        return ExtractionResult(
            success=False, 
            error_message="URL não é do weekseries.info"
        )
    
    # Early return com URL do cache se disponível
    if use_cache:
        cached_url = get_cached_stream_url(page_url)
        if cached_url:
            # Extrai informações do episódio
            episode_data = extract_episode_info(page_url)
            episode_info = None
            if episode_data:
                episode_info = EpisodeInfo(
                    series_name=episode_data['series_name'],
                    season=episode_data['season'],
                    episode=episode_data['episode'],
                    original_url=episode_data['original_url']
                )
            
            return ExtractionResult(
                success=True,
                stream_url=cached_url,
                referer_url=page_url,
                episode_info=episode_info
            )
    
    # Early return para falha na requisição
    content = http_client.fetch(page_url, get_default_headers())
    if not content:
        return ExtractionResult(
            success=False,
            error_message="Falha ao obter conteúdo da página"
        )
    
    # Early return para falha no parsing
    encoded_url = html_parser.parse_stream_url(content)
    if not encoded_url:
        return ExtractionResult(
            success=False,
            error_message="URL de streaming não encontrada na página"
        )
    
    # Early return para falha na decodificação
    stream_url = base64_decoder.decode(encoded_url)
    if not stream_url:
        return ExtractionResult(
            success=False,
            error_message="Falha ao decodificar URL base64"
        )
    
    # Extrai informações do episódio
    episode_data = extract_episode_info(page_url)
    episode_info = None
    if episode_data:
        episode_info = EpisodeInfo(
            series_name=episode_data['series_name'],
            season=episode_data['season'],
            episode=episode_data['episode'],
            original_url=episode_data['original_url']
        )
    
    # Armazena no cache se extração foi bem-sucedida
    if use_cache:
        cache_stream_url(page_url, stream_url)
    
    return ExtractionResult(
        success=True,
        stream_url=stream_url,
        referer_url=page_url,
        episode_info=episode_info
    )


def get_default_headers() -> dict:
    """
    Retorna headers padrão para requisições
    
    Returns:
        Dict com headers HTTP padrão
    """
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Referer': 'https://www.weekseries.info/',
        'Origin': 'https://www.weekseries.info',
        'Accept': '*/*',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
    }


# Implementações concretas dos protocolos

class UrllibHttpClient:
    """Implementação do HttpClient usando urllib"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    def fetch(self, url: str, headers: dict) -> Optional[str]:
        """
        Faz requisição HTTP usando urllib com early return
        
        Args:
            url: URL para requisição
            headers: Headers HTTP
            
        Returns:
            Conteúdo da página ou None se falhar
        """
        if not url:
            return None
        
        if not headers:
            return None
        
        try:
            req = urllib.request.Request(url)
            
            # Adiciona headers
            for key, value in headers.items():
                req.add_header(key, value)
            
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return response.read().decode('utf-8')
                
        except (urllib.error.URLError, urllib.error.HTTPError, UnicodeDecodeError) as e:
            logger.error(f"Erro na requisição HTTP: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado na requisição: {e}")
            return None


class RegexHtmlParser:
    """Implementação do HtmlParser usando regex"""
    
    def parse_stream_url(self, content: str) -> Optional[str]:
        """
        Parseia HTML/JavaScript para encontrar URL base64 com early return
        
        Args:
            content: Conteúdo HTML da página
            
        Returns:
            URL base64 encontrada ou None
        """
        if not content:
            return None
        
        # Padrões para encontrar URLs base64 no JavaScript/HTML
        patterns = [
            # Padrão comum: variável JavaScript com base64
            r'(?:src|url|stream|video)\s*[:=]\s*["\']([A-Za-z0-9+/]{20,}={0,2})["\']',
            # Padrão em atributos data-*
            r'data-[^=]*=\s*["\']([A-Za-z0-9+/]{20,}={0,2})["\']',
            # Padrão em strings JavaScript
            r'["\']([A-Za-z0-9+/]{40,}={0,2})["\']',
            # Padrão mais genérico para base64 longo
            r'([A-Za-z0-9+/]{50,}={0,2})'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            
            for match in matches:
                # Verifica se parece ser uma URL base64 válida
                if self._is_likely_stream_url(match):
                    return match
        
        return None
    
    def _is_likely_stream_url(self, base64_string: str) -> bool:
        """
        Verifica se string base64 provavelmente contém URL de streaming
        
        Args:
            base64_string: String base64 a ser verificada
            
        Returns:
            True se provavelmente for URL de streaming
        """
        if not base64_string:
            return False
        
        if len(base64_string) < 20:
            return False
        
        # Tenta decodificar para verificar se contém URL
        try:
            decoded = decode_base64_url(base64_string)
            if not decoded:
                return False
            
            # Verifica se contém indicadores de URL de streaming
            stream_indicators = ['.m3u8', 'stream', 'video', 'http']
            return any(indicator in decoded.lower() for indicator in stream_indicators)
            
        except Exception:
            return False


class StandardBase64Decoder:
    """Implementação do Base64Decoder usando função existente"""
    
    def decode(self, encoded: str) -> Optional[str]:
        """
        Decodifica string base64 usando early return
        
        Args:
            encoded: String base64 codificada
            
        Returns:
            String decodificada ou None se falhar
        """
        if not encoded:
            return None
        
        # Reutiliza função existente do utils.py
        return decode_base64_url(encoded)

# Funções puras auxiliares

def find_base64_patterns(content: str) -> list[str]:
    """
    Encontra todos os padrões base64 no conteúdo usando early return
    
    Args:
        content: Conteúdo HTML/JavaScript
        
    Returns:
        Lista de strings base64 encontradas
    """
    if not content:
        return []
    
    patterns = [
        r'(?:src|url|stream|video)\s*[:=]\s*["\']([A-Za-z0-9+/]{20,}={0,2})["\']',
        r'data-[^=]*=\s*["\']([A-Za-z0-9+/]{20,}={0,2})["\']',
        r'["\']([A-Za-z0-9+/]{40,}={0,2})["\']',
        r'([A-Za-z0-9+/]{50,}={0,2})'
    ]
    
    found_patterns = []
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        found_patterns.extend(matches)
    
    return found_patterns


def filter_stream_candidates(base64_strings: list[str]) -> list[str]:
    """
    Filtra candidatos que provavelmente são URLs de streaming
    
    Args:
        base64_strings: Lista de strings base64
        
    Returns:
        Lista filtrada de candidatos válidos
    """
    if not base64_strings:
        return []
    
    candidates = []
    
    for b64_string in base64_strings:
        if is_valid_stream_candidate(b64_string):
            candidates.append(b64_string)
    
    return candidates


def is_valid_stream_candidate(base64_string: str) -> bool:
    """
    Verifica se string base64 é candidata válida para URL de streaming
    
    Args:
        base64_string: String base64 a ser verificada
        
    Returns:
        True se for candidata válida
    """
    if not base64_string:
        return False
    
    if len(base64_string) < 20:
        return False
    
    try:
        decoded = decode_base64_url(base64_string)
        if not decoded:
            return False
        
        # Verifica indicadores de URL de streaming
        stream_indicators = ['.m3u8', 'stream', 'video', 'http']
        has_indicator = any(indicator in decoded.lower() for indicator in stream_indicators)
        
        # Verifica se parece ser uma URL válida
        looks_like_url = decoded.startswith(('http://', 'https://'))
        
        return has_indicator and looks_like_url
        
    except Exception:
        return False


def create_extraction_dependencies() -> dict:
    """
    Cria dependências padrão para extração
    
    Returns:
        Dict com dependências configuradas
    """
    return {
        'http_client': UrllibHttpClient(),
        'html_parser': RegexHtmlParser(),
        'base64_decoder': StandardBase64Decoder(),
        'url_validator': validate_weekseries_url
    }