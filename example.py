#!/usr/bin/env python3
"""
Exemplo de uso do WeekSeries Downloader como biblioteca
"""

from weekseries_downloader.downloader import download_hls_video
from weekseries_downloader.utils import decode_base64_url, sanitize_filename
from weekseries_downloader.url_detector import detect_url_type, UrlType, validate_weekseries_url
from weekseries_downloader.extractor import extract_stream_url, create_extraction_dependencies


def main():
    # Exemplo 1: Usando URL do weekseries.info (NOVO)
    print("=== Exemplo 1: URL do WeekSeries.info ===")
    weekseries_url = "https://www.weekseries.info/series/the-good-doctor/temporada-1/episodio-01"
    
    # Detecta tipo de URL
    url_type = detect_url_type(weekseries_url)
    print(f"Tipo de URL detectado: {url_type}")
    
    if url_type == UrlType.WEEKSERIES:
        # Extrai URL de streaming
        dependencies = create_extraction_dependencies()
        result = extract_stream_url(weekseries_url, **dependencies)
        
        if result.success:
            print(f"✅ URL de streaming extraída: {result.stream_url}")
            print(f"📺 Episódio: {result.episode_info}")
            print(f"🔗 Referer: {result.referer_url}")
            
            # Exemplo de download (comentado)
            # output_file = f"{result.episode_info.filename_safe_name}.mp4"
            # success = download_hls_video(result.stream_url, output_file, referer=result.referer_url)
            # print(f"Download {'bem-sucedido' if success else 'falhou'}")
        else:
            print(f"❌ Falha na extração: {result.error_message}")
    
    # Exemplo 2: Usando URL direta de streaming
    print("\n=== Exemplo 2: URL Direta de Streaming ===")
    direct_url = "https://example.com/stream.m3u8"  # Substitua pela URL real
    url_type = detect_url_type(direct_url)
    print(f"Tipo de URL detectado: {url_type}")
    
    if url_type == UrlType.DIRECT_STREAM:
        print("✅ URL direta detectada, pode usar diretamente para download")
        # success = download_hls_video(direct_url, "video_direto.mp4")
        # print(f"Download {'bem-sucedido' if success else 'falhou'}")
    
    # Exemplo 3: Usando URL codificada em base64
    print("\n=== Exemplo 3: URL Base64 ===")
    encoded_url = "aHR0cHM6Ly9leGFtcGxlLmNvbS9zdHJlYW0ubTN1OA=="  # exemplo
    url_type = detect_url_type(encoded_url)
    print(f"Tipo de URL detectado: {url_type}")
    
    if url_type == UrlType.BASE64:
        decoded_url = decode_base64_url(encoded_url)
        print(f"URL decodificada: {decoded_url}")
    
    # Exemplo 4: Validação de URLs
    print("\n=== Exemplo 4: Validação de URLs ===")
    test_urls = [
        "https://www.weekseries.info/series/the-good-doctor/temporada-1/episodio-01",
        "https://example.com/stream.m3u8",
        "aHR0cHM6Ly9leGFtcGxlLmNvbS9zdHJlYW0ubTN1OA==",
        "https://invalid-url.com"
    ]
    
    for test_url in test_urls:
        url_type = detect_url_type(test_url)
        is_weekseries = validate_weekseries_url(test_url)
        print(f"URL: {test_url[:50]}...")
        print(f"  Tipo: {url_type}")
        print(f"  É WeekSeries: {is_weekseries}")
        print()
    
    # Exemplo 5: Sanitização de nome de arquivo
    print("=== Exemplo 5: Sanitização ===")
    unsafe_filename = 'Série: "O Bom Doutor" - S02E16.mp4'
    safe_filename = sanitize_filename(unsafe_filename)
    print(f"Nome original: {unsafe_filename}")
    print(f"Nome sanitizado: {safe_filename}")


if __name__ == "__main__":
    main()