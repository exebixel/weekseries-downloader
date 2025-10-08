"""
Interface de linha de comando para o WeekSeries Downloader
"""

import sys
import click
from typing import Optional, Tuple

from weekseries_downloader.utils import decode_base64_url, sanitize_filename
from weekseries_downloader.downloader import download_hls_video
from weekseries_downloader.url_detector import detect_url_type, UrlType
from weekseries_downloader.extractor import extract_stream_url, create_extraction_dependencies
from weekseries_downloader.models import DownloadConfig


def create_dependencies() -> dict:
    """Cria dependências para injeção"""
    return create_extraction_dependencies()


def process_url_input(
    url: Optional[str], 
    encoded: Optional[str],
    dependencies: dict
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Processa input de URL usando early returns
    
    Args:
        url: URL fornecida pelo usuário
        encoded: URL base64 codificada
        dependencies: Dependências para extração
        
    Returns:
        Tupla (stream_url, error_message, referer_url)
    """
    
    # Early return para URL codificada
    if encoded:
        click.echo("🔓 Decodificando URL...")
        decoded = decode_base64_url(encoded)
        if not decoded:
            return None, "Falha ao decodificar URL base64", None
        return decoded, None, None
    
    # Early return se não há URL
    if not url:
        return None, "Você precisa fornecer --url ou --encoded", None
    
    url_type = detect_url_type(url)
    
    # Early return para URL direta de streaming
    if url_type == UrlType.DIRECT_STREAM:
        return url, None, None
    
    # Early return para URL do weekseries
    if url_type == UrlType.WEEKSERIES:
        click.echo("🔍 Extraindo URL de streaming...")
        
        # Verifica cache primeiro
        from weekseries_downloader.cache import get_cached_stream_url
        cached_url = get_cached_stream_url(url)
        if cached_url:
            click.echo("⚡ URL encontrada no cache")
        
        result = extract_stream_url(url, **dependencies)
        
        if not result.success:
            return None, result.error_message, None
        
        # Indica se veio do cache ou foi extraída
        if not cached_url:
            click.echo("✅ URL de streaming extraída com sucesso")
        
        # Sugere nome de arquivo baseado no episódio se disponível
        if result.episode_info:
            click.echo(f"📺 Detectado: {result.episode_info}")
        
        return result.stream_url, None, result.referer_url
    
    # Early return para base64 direto
    if url_type == UrlType.BASE64:
        click.echo("🔓 Decodificando URL base64...")
        decoded = decode_base64_url(url)
        if not decoded:
            return None, "Falha ao decodificar URL base64", None
        return decoded, None, None
    
    return None, f"Tipo de URL não suportado. Use URLs do weekseries.info ou URLs de streaming direto.", None


@click.command()
@click.option("--url", "-u", help="URL do weekseries.info ou stream m3u8 direto")
@click.option("--encoded", "-e", help="URL do stream codificada em base64")
@click.option(
    "--output",
    "-o",
    default="video.mp4",
    help="Nome do arquivo de saída (padrão: video.mp4)",
)
@click.option(
    "--referer",
    "-r",
    help="URL da página de referência (padrão: https://www.weekseries.info/)",
)
@click.option("--no-convert", is_flag=True, help="Não converter para MP4, manter apenas .ts")
@click.version_option(version="0.1.0", prog_name="weekseries-dl")
def main(url, encoded, output, referer, no_convert):
    """
    WeekSeries Downloader - Baixar vídeos do WeekSeries usando Python puro

    Exemplos:

    \b
    # Baixar usando URL do weekseries.info (NOVO):
    weekseries-dl --url "https://www.weekseries.info/series/the-good-doctor/temporada-1/episodio-01"

    \b
    # Baixar usando URL base64 codificada:
    weekseries-dl --encoded "aHR0cHM6Ly9zZXJpZXMudmlkbWFuaWl4LnNob3AvVC90aGUtZ29vZC1kb2N0b3IvMDItdGVtcG9yYWRhLzE2L3N0cmVhbS5tM3U4"

    \b
    # Baixar usando URL direta de streaming:
    weekseries-dl --url "https://series.vidmaniix.shop/T/the-good-doctor/02-temporada/16/stream.m3u8"

    \b
    # Com nome de arquivo personalizado:
    weekseries-dl --url "https://www.weekseries.info/series/..." --output "meu_episodio.mp4"

    \b
    # Manter apenas arquivo .ts (sem conversão):
    weekseries-dl --url "..." --no-convert
    """

    # Processa URL usando padrão funcional
    dependencies = create_dependencies()
    
    stream_url, error, auto_referer = process_url_input(url, encoded, dependencies)
    
    if error:
        click.echo(f"❌ {error}", err=True)
        click.echo("\nFormatos suportados:")
        click.echo("  • URLs do weekseries.info: https://www.weekseries.info/series/[serie]/temporada-[numero]/episodio-[numero]")
        click.echo("  • URLs de streaming direto: https://exemplo.com/stream.m3u8")
        click.echo("  • URLs base64 codificadas")
        click.echo("\nUse --help para ver exemplos completos")
        sys.exit(1)

    # Sanitiza nome do arquivo
    output_file = sanitize_filename(output)

    # Define extensão baseado nas opções
    if no_convert:
        if not output_file.endswith(".ts"):
            output_file = output_file.replace(".mp4", ".ts") if output_file.endswith(".mp4") else output_file + ".ts"
    else:
        if not output_file.endswith(".mp4") and not output_file.endswith(".ts"):
            output_file += ".mp4"

    # Define referer automaticamente se não fornecido
    final_referer = referer or auto_referer
    
    # Baixa o vídeo
    convert_mp4 = not no_convert
    success = download_hls_video(stream_url, output_file, referer=final_referer, convert_mp4=convert_mp4)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
