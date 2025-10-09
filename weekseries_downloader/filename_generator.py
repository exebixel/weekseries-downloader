"""
Módulo para geração automática de nomes de arquivos
"""

import re
from typing import Optional
from urllib.parse import urlparse

from weekseries_downloader.models import EpisodeInfo
from weekseries_downloader.logging_config import get_logger

logger = get_logger(__name__)


def generate_automatic_filename(
    original_url: Optional[str],
    episode_info: Optional[EpisodeInfo],
    user_output: str,
    no_convert: bool = False
) -> str:
    """
    Gera nome de arquivo automaticamente baseado na URL e informações do episódio
    
    Args:
        original_url: URL original fornecida pelo usuário
        episode_info: Informações do episódio extraídas
        user_output: Output fornecido pelo usuário
        no_convert: Se deve manter como .ts
        
    Returns:
        Nome de arquivo final
    """
    # Se usuário forneceu nome específico (não é o padrão), usa ele
    if user_output != "video.mp4":
        logger.debug(f"Usando nome personalizado: {user_output}")
        return _adjust_extension(user_output, no_convert)
    
    # Prioridade 1: Nome baseado em informações do episódio
    if episode_info:
        filename = f"{episode_info.filename_safe_name}.mp4"
        logger.info(f"Nome automático baseado no episódio: {filename}")
        return _adjust_extension(filename, no_convert)
    
    # Prioridade 2: Nome extraído da URL de streaming
    extracted_name = extract_filename_from_stream_url(original_url)
    if extracted_name:
        logger.info(f"Nome baseado na URL: {extracted_name}")
        return _adjust_extension(extracted_name, no_convert)
    
    # Fallback: nome padrão
    logger.debug("Usando nome padrão: video.mp4")
    return _adjust_extension("video.mp4", no_convert)


def extract_filename_from_stream_url(url: Optional[str]) -> Optional[str]:
    """
    Extrai nome de arquivo da URL de streaming usando múltiplos padrões
    
    Args:
        url: URL para extrair nome
        
    Returns:
        Nome de arquivo extraído ou None
    """
    if not url:
        return None
    
    logger.debug(f"Extraindo nome da URL: {url}")
    
    # Verifica se é URL de streaming
    if not _is_streaming_url(url):
        return None
    
    # Tenta diferentes estratégias de extração
    strategies = [
        _extract_from_temporada_pattern,
        _extract_from_season_pattern,
        _extract_from_path_segments,
        _extract_from_domain_and_path
    ]
    
    for strategy in strategies:
        result = strategy(url)
        if result:
            logger.debug(f"Nome extraído usando {strategy.__name__}: {result}")
            return result
    
    logger.debug("Nenhum padrão reconhecido na URL")
    return None


def _is_streaming_url(url: str) -> bool:
    """Verifica se URL é de streaming"""
    streaming_indicators = [".m3u8", "stream", "playlist", "video", "media"]
    return any(indicator in url.lower() for indicator in streaming_indicators)


def _extract_from_temporada_pattern(url: str) -> Optional[str]:
    """
    Extrai nome usando padrão serie/temporada/episodio
    
    Exemplos:
    - /the-good-doctor/02-temporada/16/stream.m3u8
    - /breaking-bad/05-temporada/14/playlist.m3u8
    """
    parts = url.split("/")
    
    for i, part in enumerate(parts):
        if "temporada" in part.lower() and i > 0 and i < len(parts) - 1:
            serie = _clean_name(parts[i-1])
            temporada = _clean_name(part)
            episodio = _clean_name(parts[i+1]) if i+1 < len(parts) else "01"
            return f"{serie}_{temporada}_{episodio}.mp4"
    
    return None


def _extract_from_season_pattern(url: str) -> Optional[str]:
    """
    Extrai nome usando padrão serie/season-XX/episode-XX
    
    Exemplos:
    - /the-office/season-09/episode-23/stream.m3u8
    - /friends/season-10/episode-01/playlist.m3u8
    """
    parts = url.split("/")
    
    for i, part in enumerate(parts):
        if "season" in part.lower() and i > 0 and i < len(parts) - 1:
            serie = _clean_name(parts[i-1])
            season = _clean_name(part)
            episode = _clean_name(parts[i+1]) if i+1 < len(parts) else "01"
            return f"{serie}_{season}_{episode}.mp4"
    
    return None


def _extract_from_path_segments(url: str) -> Optional[str]:
    """
    Extrai nome dos últimos segmentos do path
    
    Exemplos:
    - /content/stranger-things/04-temporada/09/index.m3u8
    - /videos/game-of-thrones/08-temporada/06/stream.m3u8
    """
    parts = url.split("/")
    
    # Filtra partes relevantes (remove arquivo final e partes vazias)
    relevant_parts = [
        p for p in parts[-4:-1] 
        if p and not p.endswith(('.m3u8', '.ts', '.mp4')) and p != "stream"
    ]
    
    if len(relevant_parts) >= 2:
        # Assume que o primeiro é série, outros são temporada/episódio
        serie = _clean_name(relevant_parts[0])
        extras = "_".join(_clean_name(p) for p in relevant_parts[1:])
        return f"{serie}_{extras}.mp4"
    
    return None


def _extract_from_domain_and_path(url: str) -> Optional[str]:
    """
    Extrai nome usando domínio e path como fallback
    
    Exemplos:
    - https://example.com/simple/stream.m3u8 -> example_com_simple.mp4
    """
    try:
        parsed = urlparse(url)
        domain_parts = parsed.netloc.split(".")
        path_parts = [p for p in parsed.path.split("/") if p and not p.endswith(('.m3u8', '.ts'))]
        
        # Usa parte principal do domínio + últimos segmentos do path
        if domain_parts and path_parts:
            domain_name = _clean_name(domain_parts[0])
            path_name = "_".join(_clean_name(p) for p in path_parts[-2:])
            return f"{domain_name}_{path_name}.mp4"
    
    except Exception as e:
        logger.debug(f"Erro ao extrair de domínio/path: {e}")
    
    return None


def _clean_name(name: str) -> str:
    """
    Limpa nome para uso em arquivo
    
    Args:
        name: Nome a ser limpo
        
    Returns:
        Nome limpo e seguro para arquivo
    """
    if not name:
        return ""
    
    # Remove caracteres especiais e substitui por underscore
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', name)
    
    # Substitui espaços e hífens por underscores para consistência
    cleaned = cleaned.replace(' ', '_').replace('-', '_')
    
    # Remove múltiplos underscores consecutivos
    cleaned = re.sub(r'_+', '_', cleaned)
    
    # Remove underscores no início e fim
    cleaned = cleaned.strip('_')
    
    return cleaned.lower()


def _adjust_extension(filename: str, no_convert: bool) -> str:
    """
    Ajusta extensão do arquivo baseado na opção de conversão
    
    Args:
        filename: Nome do arquivo
        no_convert: Se deve manter como .ts
        
    Returns:
        Nome com extensão ajustada
    """
    if no_convert:
        if filename.endswith(".mp4"):
            return filename.replace(".mp4", ".ts")
        elif not filename.endswith(".ts"):
            return filename + ".ts"
    else:
        if not filename.endswith((".mp4", ".ts")):
            return filename + ".mp4"
    
    return filename


def suggest_filename_from_episode_info(episode_info: EpisodeInfo, no_convert: bool = False) -> str:
    """
    Sugere nome de arquivo baseado em informações do episódio
    
    Args:
        episode_info: Informações do episódio
        no_convert: Se deve usar extensão .ts
        
    Returns:
        Nome de arquivo sugerido
    """
    base_name = episode_info.filename_safe_name
    extension = ".ts" if no_convert else ".mp4"
    return f"{base_name}{extension}"


def validate_filename(filename: str) -> str:
    """
    Valida e corrige nome de arquivo
    
    Args:
        filename: Nome a ser validado
        
    Returns:
        Nome de arquivo válido
    """
    if not filename:
        return "video.mp4"
    
    # Remove caracteres inválidos
    valid_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Garante que não está vazio após limpeza
    if not valid_name.strip():
        return "video.mp4"
    
    # Garante extensão
    if not valid_name.endswith(('.mp4', '.ts')):
        valid_name += '.mp4'
    
    return valid_name


def get_filename_suggestions(url: Optional[str], episode_info: Optional[EpisodeInfo]) -> list[str]:
    """
    Obtém múltiplas sugestões de nome de arquivo
    
    Args:
        url: URL original
        episode_info: Informações do episódio
        
    Returns:
        Lista de sugestões de nome
    """
    suggestions = []
    
    # Sugestão baseada no episódio
    if episode_info:
        suggestions.append(suggest_filename_from_episode_info(episode_info))
    
    # Sugestão baseada na URL
    url_name = extract_filename_from_stream_url(url)
    if url_name:
        suggestions.append(url_name)
    
    # Sugestão padrão
    if not suggestions:
        suggestions.append("video.mp4")
    
    return suggestions