#!/usr/bin/env python3
"""
Teste de integração para verificar funcionalidade básica
"""

from weekseries_downloader.url_detector import detect_url_type, UrlType, validate_weekseries_url
from weekseries_downloader.extractor import create_extraction_dependencies
from weekseries_downloader.cache import get_cache_stats, clear_url_cache


def test_url_detection():
    """Testa detecção de tipos de URL"""
    print("=== Teste de Detecção de URLs ===")
    
    test_cases = [
        ("https://www.weekseries.info/series/the-good-doctor/temporada-1/episodio-01", UrlType.WEEKSERIES),
        ("https://example.com/stream.m3u8", UrlType.DIRECT_STREAM),
        ("aHR0cHM6Ly9leGFtcGxlLmNvbS9zdHJlYW0ubTN1OA==", UrlType.BASE64),
        ("https://invalid-url.com", UrlType.UNKNOWN),
        ("", UrlType.UNKNOWN),
    ]
    
    for url, expected in test_cases:
        detected = detect_url_type(url)
        status = "✅" if detected == expected else "❌"
        print(f"{status} {url[:50]}... -> {detected}")
    
    print()


def test_weekseries_validation():
    """Testa validação específica de URLs do weekseries"""
    print("=== Teste de Validação WeekSeries ===")
    
    valid_urls = [
        "https://www.weekseries.info/series/the-good-doctor/temporada-1/episodio-01",
        "http://weekseries.info/series/breaking-bad/temporada-5/episodio-16",
    ]
    
    invalid_urls = [
        "https://other-site.com/series/show/temporada-1/episodio-01",
        "https://www.weekseries.info/series/show",  # incompleto
        "not-a-url",
        "",
    ]
    
    for url in valid_urls:
        is_valid = validate_weekseries_url(url)
        status = "✅" if is_valid else "❌"
        print(f"{status} VÁLIDA: {url}")
    
    for url in invalid_urls:
        is_valid = validate_weekseries_url(url)
        status = "✅" if not is_valid else "❌"
        print(f"{status} INVÁLIDA: {url}")
    
    print()


def test_dependencies_creation():
    """Testa criação de dependências"""
    print("=== Teste de Criação de Dependências ===")
    
    try:
        deps = create_extraction_dependencies()
        
        required_keys = ['http_client', 'html_parser', 'base64_decoder', 'url_validator']
        
        for key in required_keys:
            if key in deps:
                print(f"✅ {key}: {type(deps[key]).__name__}")
            else:
                print(f"❌ {key}: AUSENTE")
        
        print()
        
    except Exception as e:
        print(f"❌ Erro ao criar dependências: {e}")
        print()


def test_cache_functionality():
    """Testa funcionalidade básica do cache"""
    print("=== Teste de Cache ===")
    
    try:
        # Limpa cache
        clear_url_cache()
        
        # Verifica estatísticas iniciais
        stats = get_cache_stats()
        print(f"✅ Cache limpo - Tamanho: {stats['size']}")
        
        # Testa importação das funções de cache
        from weekseries_downloader.cache import cache_stream_url, get_cached_stream_url
        
        # Testa armazenamento
        test_url = "https://www.weekseries.info/series/test/temporada-1/episodio-01"
        test_stream = "https://example.com/stream.m3u8"
        
        success = cache_stream_url(test_url, test_stream)
        print(f"✅ Armazenamento no cache: {'sucesso' if success else 'falha'}")
        
        # Testa recuperação
        cached = get_cached_stream_url(test_url)
        match = cached == test_stream
        print(f"✅ Recuperação do cache: {'sucesso' if match else 'falha'}")
        
        # Verifica estatísticas finais
        stats = get_cache_stats()
        print(f"✅ Cache após teste - Tamanho: {stats['size']}")
        
        print()
        
    except Exception as e:
        print(f"❌ Erro no teste de cache: {e}")
        print()


def main():
    """Executa todos os testes"""
    print("🧪 Executando Testes de Integração\n")
    
    test_url_detection()
    test_weekseries_validation()
    test_dependencies_creation()
    test_cache_functionality()
    
    print("✅ Testes de integração concluídos!")
    print("\n💡 Para testar extração real, use:")
    print("   python example.py")
    print("   ou")
    print("   weekseries-dl --url 'https://www.weekseries.info/series/...'")


if __name__ == "__main__":
    main()