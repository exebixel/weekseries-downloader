"""
Módulo principal para download de vídeos HLS
"""

import os
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import urljoin
from typing import List, Optional

from weekseries_downloader.utils import create_request, check_ffmpeg
from weekseries_downloader.converter import convert_to_mp4
from weekseries_downloader.logging_config import get_logger

logger = get_logger(__name__)


def download_m3u8_playlist(url: str, referer: Optional[str] = None) -> Optional[str]:
    """
    Baixa o conteúdo do arquivo m3u8

    Args:
        url: URL do arquivo m3u8
        referer: URL de referência

    Returns:
        Conteúdo do arquivo m3u8
    """
    try:
        req = create_request(url, referer)
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode("utf-8")
    except Exception as e:
        logger.error(f"Erro ao baixar playlist: {e}")
        return None


def parse_m3u8(content: str, base_url: str) -> List[str]:
    """
    Parseia arquivo m3u8 e extrai URLs dos segmentos

    Args:
        content: Conteúdo do arquivo m3u8
        base_url: URL base para resolver URLs relativas

    Returns:
        Lista de URLs de segmentos
    """
    segments = []
    lines = content.split("\n")

    for line in lines:
        line = line.strip()
        # Ignora comentários e linhas vazias
        if not line or line.startswith("#"):
            # Verifica se é uma playlist master (com outras resoluções)
            if line.startswith("#EXT-X-STREAM-INF"):
                logger.info("Playlist master detectada (múltiplas qualidades)")
            continue

        # Se for URL relativa, converte para absoluta
        if not line.startswith("http"):
            segment_url = urljoin(base_url, line)
        else:
            segment_url = line

        segments.append(segment_url)

    return segments


def download_segment(url: str, referer: Optional[str] = None) -> Optional[bytes]:
    """
    Baixa um segmento individual

    Args:
        url: URL do segmento
        referer: URL de referência

    Returns:
        Conteúdo binário do segmento
    """
    try:
        req = create_request(url, referer)
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read()
    except Exception as e:
        logger.error(f"Erro ao baixar segmento {url}: {e}")
        return None


def download_hls_video(
    m3u8_url: str,
    output_file: str,
    referer: Optional[str] = None,
    convert_mp4: bool = True,
) -> bool:
    """
    Baixa vídeo HLS completo

    Args:
        m3u8_url: URL do arquivo m3u8
        output_file: Caminho do arquivo de saída
        referer: URL de referência
        convert_mp4: Se True, converte para MP4 automaticamente
    """
    logger.info(f"URL do stream: {m3u8_url}")
    logger.info(f"Salvando em: {output_file}")
    logger.info("Baixando playlist m3u8...")

    # Baixa o conteúdo da playlist
    playlist_content = download_m3u8_playlist(m3u8_url, referer)
    if not playlist_content:
        logger.error("Não foi possível baixar a playlist")
        return False

    # Verifica se é uma playlist master (com múltiplas qualidades)
    if "#EXT-X-STREAM-INF" in playlist_content:
        logger.info("Detectada playlist master com múltiplas qualidades")
        logger.info("Selecionando melhor qualidade...")

        # Extrai URLs das sub-playlists
        lines = playlist_content.split("\n")
        best_playlist_url = None

        for i, line in enumerate(lines):
            if line.startswith("#EXT-X-STREAM-INF"):
                # Próxima linha é a URL da playlist
                if i + 1 < len(lines):
                    playlist_path = lines[i + 1].strip()
                    best_playlist_url = urljoin(m3u8_url, playlist_path)
                    break

        if best_playlist_url:
            logger.info(f"Baixando playlist de qualidade: {best_playlist_url}")
            playlist_content = download_m3u8_playlist(best_playlist_url, referer)
            m3u8_url = best_playlist_url  # Atualiza URL base

            if not playlist_content:
                logger.error("Não foi possível baixar a sub-playlist")
                return False

    # Extrai URLs dos segmentos
    base_url = m3u8_url.rsplit("/", 1)[0] + "/"
    segments = parse_m3u8(playlist_content, base_url)

    if not segments:
        logger.error("Nenhum segmento encontrado na playlist")
        return False

    logger.info(f"Total de segmentos: {len(segments)}")
    logger.info("Baixando segmentos... (isso pode demorar alguns minutos)")

    # Baixa todos os segmentos
    temp_dir = Path(output_file).parent / f".tmp_{Path(output_file).stem}"
    temp_dir.mkdir(exist_ok=True)

    downloaded_segments = []

    try:
        for i, segment_url in enumerate(segments, 1):
            # Mostra progresso
            percent = (i / len(segments)) * 100
            # Log progresso a cada 10% ou no último segmento
            if i % max(1, len(segments) // 10) == 0 or i == len(segments):
                logger.info(f"Progresso: {i}/{len(segments)} ({percent:.1f}%)")

            # Baixa segmento
            segment_data = download_segment(segment_url, referer)

            if segment_data is None:
                logger.warning(f"Falha ao baixar segmento {i}, tentando continuar...")
                continue

            # Salva segmento temporário
            temp_file = temp_dir / f"segment_{i:05d}.ts"
            temp_file.write_bytes(segment_data)
            downloaded_segments.append(temp_file)

        logger.info("Todos os segmentos baixados!")
        logger.info("Juntando segmentos...")

        # Junta todos os segmentos em um único arquivo TS
        ts_file = output_file
        if convert_mp4 and output_file.endswith(".mp4"):
            # Salva temporariamente como .ts
            ts_file = output_file.replace(".mp4", ".ts")

        with open(ts_file, "wb") as outfile:
            for segment_file in downloaded_segments:
                outfile.write(segment_file.read_bytes())

        logger.info(f"Arquivo TS completo: {ts_file}")

        # Limpa arquivos temporários de segmentos
        logger.info("Limpando segmentos temporários...")
        for segment_file in downloaded_segments:
            segment_file.unlink()
        temp_dir.rmdir()

        # Converte para MP4 se solicitado
        if convert_mp4 and output_file.endswith(".mp4"):
            if not check_ffmpeg():
                logger.warning("ffmpeg não encontrado, mantendo arquivo .ts")
                logger.info("Instale ffmpeg com: brew install ffmpeg")
                logger.info(f"Ou converta manualmente: ffmpeg -i {ts_file} -c copy {output_file}")
                return True

            if convert_to_mp4(ts_file, output_file):
                # Remove arquivo .ts após conversão bem-sucedida
                logger.info("Removendo arquivo .ts temporário...")
                try:
                    os.remove(ts_file)
                    logger.info(f"Arquivo final: {output_file}")
                except Exception as e:
                    logger.warning(f"Não foi possível remover {ts_file}: {e}")
            else:
                logger.warning(f"Conversão falhou, arquivo .ts mantido: {ts_file}")

        return True

    except KeyboardInterrupt:
        logger.info("Download cancelado pelo usuário")
        logger.info("Limpando arquivos temporários...")
        for segment_file in downloaded_segments:
            if segment_file.exists():
                segment_file.unlink()
        if temp_dir.exists():
            temp_dir.rmdir()
        return False

    except Exception as e:
        logger.error(f"Erro durante o download: {e}")
        # Tenta limpar arquivos temporários
        try:
            for segment_file in downloaded_segments:
                if segment_file.exists():
                    segment_file.unlink()
            if temp_dir.exists():
                temp_dir.rmdir()
        except Exception:
            pass
        return False
