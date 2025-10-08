#!/usr/bin/env python3
"""
Exemplo de uso do WeekSeries Downloader como biblioteca
"""

from weekseries_downloader.downloader import download_hls_video
from weekseries_downloader.utils import decode_base64_url, sanitize_filename


def main():
    # Exemplo 1: Usando URL direta
    print("=== Exemplo 1: URL Direta ===")
    url = "https://example.com/stream.m3u8"  # Substitua pela URL real
    output_file = "video_exemplo.mp4"
    
    # success = download_hls_video(url, output_file)
    # print(f"Download {'bem-sucedido' if success else 'falhou'}")
    
    # Exemplo 2: Usando URL codificada em base64
    print("\n=== Exemplo 2: URL Base64 ===")
    encoded_url = "aHR0cHM6Ly9leGFtcGxlLmNvbS9zdHJlYW0ubTN1OA=="  # exemplo
    decoded_url = decode_base64_url(encoded_url)
    print(f"URL decodificada: {decoded_url}")
    
    # Exemplo 3: Sanitização de nome de arquivo
    print("\n=== Exemplo 3: Sanitização ===")
    unsafe_filename = 'Série: "O Bom Doutor" - S02E16.mp4'
    safe_filename = sanitize_filename(unsafe_filename)
    print(f"Nome original: {unsafe_filename}")
    print(f"Nome sanitizado: {safe_filename}")


if __name__ == "__main__":
    main()