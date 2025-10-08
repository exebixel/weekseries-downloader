"""
Módulo para conversão de vídeos
"""

import subprocess
from weekseries_downloader.logging_config import get_logger

logger = get_logger(__name__)


def convert_to_mp4(input_file: str, output_file: str) -> bool:
    """
    Converte arquivo TS para MP4 usando ffmpeg

    Args:
        input_file: Arquivo .ts de entrada
        output_file: Arquivo .mp4 de saída

    Returns:
        True se conversão bem-sucedida, False caso contrário
    """
    logger.info("Convertendo para MP4...")

    cmd = [
        "ffmpeg",
        "-i",
        input_file,
        "-c",
        "copy",  # Copia sem recodificar (rápido)
        "-y",  # Sobrescreve se existir
        output_file,
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f"Conversão completa! Arquivo MP4: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao converter: {e}")
        return False
