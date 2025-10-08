"""
Sistema de cache simples para URLs extraídas
"""

import time
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class CacheEntry:
    """Entrada do cache com timestamp"""
    value: Any
    timestamp: float
    ttl: float  # Time to live em segundos
    
    @property
    def is_expired(self) -> bool:
        """Verifica se entrada expirou"""
        return time.time() > (self.timestamp + self.ttl)


class SimpleCache:
    """Cache simples em memória com TTL"""
    
    def __init__(self, default_ttl: float = 300):  # 5 minutos padrão
        self._cache: Dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtém valor do cache usando early return
        
        Args:
            key: Chave do cache
            
        Returns:
            Valor armazenado ou None se não existir/expirado
        """
        if not key:
            return None
        
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        
        if entry.is_expired:
            # Remove entrada expirada
            del self._cache[key]
            return None
        
        return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """
        Armazena valor no cache usando early return
        
        Args:
            key: Chave do cache
            value: Valor a ser armazenado
            ttl: Time to live personalizado
            
        Returns:
            True se armazenado com sucesso
        """
        if not key:
            return False
        
        if value is None:
            return False
        
        effective_ttl = ttl or self._default_ttl
        
        self._cache[key] = CacheEntry(
            value=value,
            timestamp=time.time(),
            ttl=effective_ttl
        )
        
        return True
    
    def clear(self) -> None:
        """Limpa todo o cache"""
        self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """
        Remove entradas expiradas do cache
        
        Returns:
            Número de entradas removidas
        """
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)
    
    @property
    def size(self) -> int:
        """Retorna número de entradas no cache"""
        return len(self._cache)


# Cache global para URLs extraídas
_url_cache = SimpleCache(default_ttl=600)  # 10 minutos


def get_cached_stream_url(page_url: str) -> Optional[str]:
    """
    Obtém URL de streaming do cache
    
    Args:
        page_url: URL da página do weekseries
        
    Returns:
        URL de streaming ou None se não estiver em cache
    """
    return _url_cache.get(page_url)


def cache_stream_url(page_url: str, stream_url: str) -> bool:
    """
    Armazena URL de streaming no cache
    
    Args:
        page_url: URL da página do weekseries
        stream_url: URL de streaming extraída
        
    Returns:
        True se armazenado com sucesso
    """
    return _url_cache.set(page_url, stream_url)


def clear_url_cache() -> None:
    """Limpa cache de URLs"""
    _url_cache.clear()


def cleanup_expired_urls() -> int:
    """
    Remove URLs expiradas do cache
    
    Returns:
        Número de URLs removidas
    """
    return _url_cache.cleanup_expired()


def get_cache_stats() -> dict:
    """
    Obtém estatísticas do cache
    
    Returns:
        Dict com estatísticas do cache
    """
    return {
        'size': _url_cache.size,
        'expired_cleaned': cleanup_expired_urls()
    }