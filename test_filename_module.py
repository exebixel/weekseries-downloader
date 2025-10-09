#!/usr/bin/env python3
"""
Teste específico do módulo filename_generator
"""

from weekseries_downloader.filename_generator import (
    generate_automatic_filename,
    extract_filename_from_stream_url,
    get_filename_suggestions,
    suggest_filename_from_episode_info,
    validate_filename,
    _clean_name,
    _extract_from_temporada_pattern,
    _extract_from_season_pattern,
    _extract_from_path_segments,
    _extract_from_domain_and_path
)
from weekseries_downloader.models import EpisodeInfo


def test_cleaning_functions():
    """Testa funções de limpeza de nomes"""
    print("🧹 Testando Funções de Limpeza\n")
    
    test_cases = [
        ("the-good-doctor", "the_good_doctor"),
        ("Breaking Bad", "breaking_bad"),
        ("série: com/caracteres*especiais", "série_com_caracteres_especiais"),
        ("--multiple--hyphens--", "multiple_hyphens"),
        ("___underscores___", "underscores"),
        ("", ""),
    ]
    
    for input_name, expected in test_cases:
        result = _clean_name(input_name)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{input_name}' → '{result}' (esperado: '{expected}')")
    
    print()


def test_extraction_strategies():
    """Testa diferentes estratégias de extração"""
    print("🎯 Testando Estratégias de Extração\n")
    
    # Teste padrão temporada
    print("=== Padrão Temporada ===")
    temporada_urls = [
        "https://site.com/the-good-doctor/02-temporada/16/stream.m3u8",
        "https://cdn.com/breaking-bad/05-temporada/14/playlist.m3u8",
    ]
    
    for url in temporada_urls:
        result = _extract_from_temporada_pattern(url)
        print(f"✅ {url.split('/')[-4:-1]} → {result}")
    
    print()
    
    # Teste padrão season
    print("=== Padrão Season ===")
    season_urls = [
        "https://site.com/the-office/season-09/episode-23/stream.m3u8",
        "https://cdn.com/friends/season-10/episode-01/playlist.m3u8",
    ]
    
    for url in season_urls:
        result = _extract_from_season_pattern(url)
        print(f"✅ {url.split('/')[-4:-1]} → {result}")
    
    print()
    
    # Teste segmentos de path
    print("=== Segmentos de Path ===")
    path_urls = [
        "https://site.com/content/stranger-things/04-temporada/09/index.m3u8",
        "https://cdn.com/videos/game-of-thrones/08-temporada/06/stream.m3u8",
    ]
    
    for url in path_urls:
        result = _extract_from_path_segments(url)
        print(f"✅ {url.split('/')[-4:-1]} → {result}")
    
    print()
    
    # Teste domínio e path
    print("=== Domínio e Path ===")
    domain_urls = [
        "https://example.com/simple/stream.m3u8",
        "https://cdn.provider.com/media/content/stream.m3u8",
    ]
    
    for url in domain_urls:
        result = _extract_from_domain_and_path(url)
        print(f"✅ {url} → {result}")
    
    print()


def test_episode_info_integration():
    """Testa integração com EpisodeInfo"""
    print("📺 Testando Integração com EpisodeInfo\n")
    
    # Cria episódio de teste
    episode = EpisodeInfo(
        series_name="The Good Doctor",
        season=2,
        episode=16,
        original_url="https://www.weekseries.info/series/the-good-doctor/temporada-2/episodio-16"
    )
    
    print(f"Episódio: {episode}")
    print(f"Nome seguro: {episode.filename_safe_name}")
    
    # Testa sugestão de nome
    suggested_mp4 = suggest_filename_from_episode_info(episode, no_convert=False)
    suggested_ts = suggest_filename_from_episode_info(episode, no_convert=True)
    
    print(f"Sugestão MP4: {suggested_mp4}")
    print(f"Sugestão TS: {suggested_ts}")
    
    print()


def test_filename_suggestions():
    """Testa múltiplas sugestões de nome"""
    print("💡 Testando Múltiplas Sugestões\n")
    
    episode = EpisodeInfo(
        series_name="Breaking Bad",
        season=5,
        episode=14,
        original_url="https://www.weekseries.info/series/breaking-bad/temporada-5/episodio-14"
    )
    
    url = "https://series.vidmaniix.shop/T/breaking-bad/05-temporada/14/stream.m3u8"
    
    suggestions = get_filename_suggestions(url, episode)
    
    print("Sugestões de nome:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    print()


def test_filename_validation():
    """Testa validação de nomes de arquivo"""
    print("✅ Testando Validação de Nomes\n")
    
    test_cases = [
        ("arquivo_normal.mp4", "arquivo_normal.mp4"),
        ("arquivo/com\\caracteres:inválidos", "arquivo_com_caracteres_inválidos.mp4"),
        ("", "video.mp4"),
        ("   ", "video.mp4"),
        ("arquivo_sem_extensao", "arquivo_sem_extensao.mp4"),
        ("arquivo.ts", "arquivo.ts"),
    ]
    
    for input_name, expected in test_cases:
        result = validate_filename(input_name)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{input_name}' → '{result}'")
        if result != expected:
            print(f"    Esperado: '{expected}'")
    
    print()


def test_complete_workflow():
    """Testa fluxo completo de geração"""
    print("🔄 Testando Fluxo Completo\n")
    
    # Cenário 1: URL do weekseries com informações completas
    print("=== Cenário 1: WeekSeries com EpisodeInfo ===")
    episode = EpisodeInfo(
        series_name="The Good Doctor",
        season=1,
        episode=1,
        original_url="https://www.weekseries.info/series/the-good-doctor/temporada-1/episodio-01"
    )
    
    result1 = generate_automatic_filename(
        "https://www.weekseries.info/series/the-good-doctor/temporada-1/episodio-01",
        episode,
        "video.mp4",
        False
    )
    print(f"Resultado: {result1}")
    
    # Cenário 2: URL de streaming sem informações de episódio
    print("\n=== Cenário 2: Streaming sem EpisodeInfo ===")
    result2 = generate_automatic_filename(
        "https://series.vidmaniix.shop/T/breaking-bad/05-temporada/14/stream.m3u8",
        None,
        "video.mp4",
        False
    )
    print(f"Resultado: {result2}")
    
    # Cenário 3: Nome personalizado
    print("\n=== Cenário 3: Nome Personalizado ===")
    result3 = generate_automatic_filename(
        "https://www.weekseries.info/series/test/temporada-1/episodio-01",
        episode,
        "meu_episodio_favorito.mp4",
        False
    )
    print(f"Resultado: {result3}")
    
    # Cenário 4: Arquivo .ts
    print("\n=== Cenário 4: Arquivo TS ===")
    result4 = generate_automatic_filename(
        "https://www.weekseries.info/series/test/temporada-1/episodio-01",
        episode,
        "video.mp4",
        True  # no_convert = True
    )
    print(f"Resultado: {result4}")
    
    print()


if __name__ == "__main__":
    print("🧪 Testando Módulo filename_generator\n")
    
    test_cleaning_functions()
    test_extraction_strategies()
    test_episode_info_integration()
    test_filename_suggestions()
    test_filename_validation()
    test_complete_workflow()
    
    print("✅ Todos os testes do módulo concluídos!")