#!/usr/bin/env python3
"""
Teste da geração automática de nomes de arquivo
"""

from weekseries_downloader.filename_generator import (
    generate_automatic_filename, 
    extract_filename_from_stream_url,
    get_filename_suggestions,
    suggest_filename_from_episode_info
)
from weekseries_downloader.url_detector import detect_url_type, UrlType
from weekseries_downloader.extractor import create_extraction_dependencies, extract_stream_url


def test_automatic_filename_generation():
    """Testa geração automática de nomes de arquivo"""
    print("🧪 Testando Geração Automática de Nomes de Arquivo\n")
    
    # Teste 1: URL do WeekSeries com nome automático
    print("=== Teste 1: URL do WeekSeries ===")
    weekseries_url = "https://www.weekseries.info/series/the-good-doctor/temporada-1/episodio-01"
    
    # Simula extração para obter informações do episódio
    dependencies = create_extraction_dependencies()
    result = extract_stream_url(weekseries_url, **dependencies)
    
    if result.success and result.episode_info:
        suggested_name = suggest_filename_from_episode_info(result.episode_info)
        print(f"📺 Episódio detectado: {result.episode_info}")
        print(f"📝 Nome sugerido: {suggested_name}")
        
        # Testa geração automática
        auto_name = generate_automatic_filename(
            weekseries_url, 
            result.episode_info, 
            "video.mp4",  # padrão
            False
        )
        print(f"✅ Nome final: {auto_name}")
    
    print()
    
    # Teste 2: URL de streaming direto
    print("=== Teste 2: URL de Streaming Direto ===")
    stream_url = "https://series.vidmaniix.shop/T/breaking-bad/05-temporada/14/stream.m3u8"
    
    extracted_name = extract_filename_from_stream_url(stream_url)
    print(f"🔗 URL: {stream_url}")
    print(f"📝 Nome extraído: {extracted_name}")
    
    auto_name = generate_automatic_filename(
        stream_url,
        None,  # sem informações de episódio
        "video.mp4",  # padrão
        False
    )
    print(f"✅ Nome final: {auto_name}")
    
    print()
    
    # Teste 3: Nome personalizado (não deve ser alterado)
    print("=== Teste 3: Nome Personalizado ===")
    custom_name = generate_automatic_filename(
        weekseries_url,
        None,  # sem informações de episódio
        "meu_arquivo_personalizado.mp4",  # personalizado
        False
    )
    print(f"📝 Nome personalizado: meu_arquivo_personalizado.mp4")
    print(f"✅ Nome final: {custom_name}")
    
    print()
    
    # Teste 4: Extensão .ts
    print("=== Teste 4: Arquivo .ts (sem conversão) ===")
    # Simula informações de episódio para teste
    from weekseries_downloader.models import EpisodeInfo
    test_episode = EpisodeInfo(
        series_name="episodio",
        season=1,
        episode=1,
        original_url=weekseries_url
    )
    
    ts_name = generate_automatic_filename(
        weekseries_url,
        test_episode,
        "video.mp4",  # padrão
        True  # no_convert = True
    )
    print(f"📝 Nome sugerido: episodio_S01E01.mp4")
    print(f"✅ Nome final (.ts): {ts_name}")
    
    print()
    
    # Teste 5: Diferentes padrões de URL
    print("=== Teste 5: Diferentes Padrões de URL ===")
    test_urls = [
        "https://series.example.com/S/game-of-thrones/08-temporada/06/stream.m3u8",
        "https://cdn.site.com/videos/stranger-things/04-temporada/09/playlist.m3u8",
        "https://stream.provider.com/content/the-office/09-temporada/23/index.m3u8"
    ]
    
    for test_url in test_urls:
        extracted = extract_filename_from_stream_url(test_url)
        print(f"URL: {test_url.split('/')[-4:-1]}")
        print(f"Nome extraído: {extracted}")
        print()


def test_url_patterns():
    """Testa diferentes padrões de URL para extração de nomes"""
    print("🔍 Testando Padrões de URL\n")
    
    patterns = [
        "https://series.vidmaniix.shop/T/the-good-doctor/02-temporada/16/stream.m3u8",
        "https://cdn.example.com/S/breaking-bad/05-temporada/14/playlist.m3u8",
        "https://stream.site.com/content/stranger-things/04-temporada/09/index.m3u8",
        "https://video.provider.com/shows/the-office/season-09/episode-23/stream.m3u8",
        "https://example.com/simple/stream.m3u8"  # sem padrão reconhecível
    ]
    
    for pattern in patterns:
        extracted = extract_filename_from_stream_url(pattern)
        status = "✅" if extracted else "❌"
        print(f"{status} {pattern}")
        print(f"   → {extracted or 'Nenhum padrão reconhecido'}")
        print()


if __name__ == "__main__":
    test_automatic_filename_generation()
    test_url_patterns()