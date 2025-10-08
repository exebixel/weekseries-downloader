"""
Interface de linha de comando para o WeekSeries Downloader
"""

import sys
import click

from weekseries_downloader.utils import decode_base64_url, sanitize_filename
from weekseries_downloader.downloader import download_hls_video


@click.command()
@click.option("--url", "-u", help="URL direta do stream m3u8")
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
    # Baixar usando URL base64 codificada:
    weekseries-dl --encoded "aHR0cHM6Ly9zZXJpZXMudmlkbWFuaWl4LnNob3AvVC90aGUtZ29vZC1kb2N0b3IvMDItdGVtcG9yYWRhLzE2L3N0cmVhbS5tM3U4"

    \b
    # Baixar usando URL direta:
    weekseries-dl --url "https://series.vidmaniix.shop/T/the-good-doctor/02-temporada/16/stream.m3u8"

    \b
    # Com referer específico:
    weekseries-dl --url "..." --referer "https://www.weekseries.info/series/the-good-doctor/temporada-2/episodio-16"

    \b
    # Manter apenas arquivo .ts (sem conversão):
    weekseries-dl --url "..." --no-convert
    """

    # Determina URL do stream
    stream_url = None

    if encoded:
        click.echo("🔓 Decodificando URL...")
        stream_url = decode_base64_url(encoded)
        if not stream_url:
            click.echo("❌ Falha ao decodificar URL base64", err=True)
            sys.exit(1)
    elif url:
        stream_url = url
    else:
        click.echo("❌ Você precisa fornecer --url ou --encoded", err=True)
        click.echo("\nUse --help para ver exemplos de uso")
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

    # Baixa o vídeo
    convert_mp4 = not no_convert
    success = download_hls_video(stream_url, output_file, referer=referer, convert_mp4=convert_mp4)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
