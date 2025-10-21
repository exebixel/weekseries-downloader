"""
Interface de linha de comando para o WeekSeries Downloader
"""

import sys
import click
from pathlib import Path
from typing import Optional, Tuple

from weekseries_downloader.models import EpisodeInfo
from weekseries_downloader.url_processing import URLParser, URLType, URLDecoder, URLExtractor
from weekseries_downloader.download import HLSDownloader
from weekseries_downloader.output import FilenameGenerator
from weekseries_downloader.infrastructure import LoggingConfig


def process_url_input(url: Optional[str], encoded: Optional[str]) -> Tuple[Optional[str], Optional[str], Optional[str], Optional["EpisodeInfo"]]:
    """
    Processa input de URL usando early returns

    Args:
        url: URL fornecida pelo usuário
        encoded: URL base64 codificada

    Returns:
        Tupla (stream_url, error_message, referer_url, episode_info)
    """

    # Early return para URL codificada
    if encoded:
        click.echo("🔓 Decodificando URL...")
        decoded = URLDecoder.decode_base64(encoded)
        if not decoded:
            return None, "Falha ao decodificar URL base64", None, None
        return decoded, None, None, None

    # Early return se não há URL
    if not url:
        return None, "Você precisa fornecer --url ou --encoded", None, None

    url_type = URLParser.detect_url_type(url)

    # Early return para URL direta de streaming
    if url_type == URLType.DIRECT_STREAM:
        return url, None, None, None

    # Early return para URL do weekseries
    if url_type == URLType.WEEKSERIES:
        click.echo("🔍 Extraindo URL de streaming...")

        extractor = URLExtractor.create_default()
        result = extractor.extract_stream_url(url)

        if not result.success:
            return None, result.error_message, None, None

        click.echo("✅ URL de streaming extraída com sucesso")

        # Retorna informações do episódio para geração de nome
        if result.episode_info:
            click.echo(f"📺 Detectado: {result.episode_info}")

        return result.stream_url, None, result.referer_url, result.episode_info

    # Early return para base64 direto
    if url_type == URLType.BASE64:
        click.echo("🔓 Decodificando URL base64...")
        decoded = URLDecoder.decode_base64(url)
        if not decoded:
            return None, "Falha ao decodificar URL base64", None, None
        return decoded, None, None, None

    return None, f"Tipo de URL não suportado. Use URLs do weekseries.info ou URLs de streaming direto.", None, None


@click.command()
@click.option("--url", "-u", help="URL do weekseries.info ou stream m3u8 direto")
@click.option("--encoded", "-e", help="URL do stream codificada em base64")
@click.option(
    "--output",
    "-o",
    default="video.mp4",
    help="Nome do arquivo de saída (padrão: gerado automaticamente baseado na URL)",
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
    # Baixar com nome automático baseado na URL (NOVO):
    weekseries-dl --url "https://www.weekseries.info/series/the-good-doctor/temporada-1/episodio-01"
    # Resultado: the_good_doctor_S01E01.mp4

    \b
    # Baixar usando URL base64 codificada:
    weekseries-dl --encoded "aHR0cHM6Ly9zZXJpZXMudmlkbWFuaWl4LnNob3AvVC90aGUtZ29vZC1kb2N0b3IvMDItdGVtcG9yYWRhLzE2L3N0cmVhbS5tM3U4"

    \b
    # Baixar usando URL direta de streaming:
    weekseries-dl --url "https://series.vidmaniix.shop/T/the-good-doctor/02-temporada/16/stream.m3u8"
    # Resultado: the_good_doctor_02_temporada_16.mp4

    \b
    # Com nome de arquivo personalizado:
    weekseries-dl --url "https://www.weekseries.info/series/..." --output "meu_episodio.mp4"

    \b
    # Manter apenas arquivo .ts (sem conversão):
    weekseries-dl --url "..." --no-convert
    # Resultado: nome_automatico.ts
    """

    # Setup logging
    LoggingConfig.setup_default()

    # Processa URL usando padrão funcional
    stream_url, error, auto_referer, episode_info = process_url_input(url, encoded)

    if error:
        click.echo(f"❌ {error}", err=True)
        click.echo("\nFormatos suportados:")
        click.echo("  • URLs do weekseries.info: https://www.weekseries.info/series/[serie]/temporada-[numero]/episodio-[numero]")
        click.echo("  • URLs de streaming direto: https://exemplo.com/stream.m3u8")
        click.echo("  • URLs base64 codificadas")
        click.echo("\nUse --help para ver exemplos completos")
        sys.exit(1)

    # Gera nome de arquivo automaticamente se necessário
    generator = FilenameGenerator()
    output_filename = generator.generate(
        stream_url=stream_url,
        episode_info=episode_info,
        user_output=output if output != "video.mp4" else None,
        default_extension=".ts" if no_convert else ".mp4",
    )

    # Valida nome do arquivo
    output_filename = FilenameGenerator.validate_filename(output_filename)
    output_path = Path(output_filename)

    # Define referer automaticamente se não fornecido
    final_referer = referer or auto_referer

    # Baixa o vídeo
    downloader = HLSDownloader.create_default()
    convert_mp4 = not no_convert
    success = downloader.download(stream_url=stream_url, output_path=output_path, referer=final_referer, convert_to_mp4=convert_mp4)

    if success:
        click.echo(f"✅ Download concluído: {output_path}")
    else:
        click.echo("❌ Falha no download", err=True)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
