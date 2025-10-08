"""
Utilitários para o WeekSeries Downloader
"""

import base64
import re
import subprocess
import urllib.request
from typing import Optional


def decode_base64_url(encoded_url: str) -> Optional[str]:
    """Decodifica URL em base64"""
    try:
        decoded = base64.b64decode(encoded_url).decode('utf-8')
        return decoded
    except Exception as e:
        print(f"Erro ao decodificar URL: {e}")
        return None


def sanitize_filename(filename: str) -> str:
    """Remove caracteres inválidos do nome do arquivo"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


def check_ffmpeg() -> bool:
    """Verifica se ffmpeg está instalado"""
    try:
        subprocess.run(['ffmpeg', '-version'],
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def create_request(url: str, referer: Optional[str] = None) -> urllib.request.Request:
    """Cria requisição com headers apropriados"""
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/131.0.0.0 Safari/537.36')

    if referer:
        req.add_header('Referer', referer)
    else:
        req.add_header('Referer', 'https://www.weekseries.info/')

    req.add_header('Origin', 'https://www.weekseries.info')
    req.add_header('Accept', '*/*')
    req.add_header('Accept-Language', 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7')

    return req