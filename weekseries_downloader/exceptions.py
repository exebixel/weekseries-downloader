"""
Exceções customizadas para o weekseries downloader
"""


class ExtractionError(Exception):
    """Erro base para extração de URLs"""

    def __init__(self, message: str, url: str = None):
        super().__init__(message)
        self.message = message
        self.url = url

    def __str__(self) -> str:
        if self.url:
            return f"{self.message} (URL: {self.url})"
        return self.message


class InvalidURLError(ExtractionError):
    """URL não segue padrão esperado"""

    def __init__(self, url: str, expected_format: str = None):
        message = f"URL inválida: {url}"
        if expected_format:
            message += f". Formato esperado: {expected_format}"
        super().__init__(message, url)


class PageNotFoundError(ExtractionError):
    """Página/episódio não encontrado"""

    def __init__(self, url: str):
        message = "Página não encontrada ou episódio não existe"
        super().__init__(message, url)


class ParsingError(ExtractionError):
    """Falha ao parsear conteúdo da página"""

    def __init__(self, url: str, details: str = None):
        message = "Falha ao encontrar URL de streaming na página"
        if details:
            message += f": {details}"
        super().__init__(message, url)


class NetworkError(ExtractionError):
    """Erro de rede durante requisição"""

    def __init__(self, url: str, original_error: Exception = None):
        message = "Erro de rede ao acessar página"
        if original_error:
            message += f": {str(original_error)}"
        super().__init__(message, url)
        self.original_error = original_error


class DecodingError(ExtractionError):
    """Falha ao decodificar URL base64"""

    def __init__(self, encoded_url: str, original_error: Exception = None):
        message = "Falha ao decodificar URL base64"
        if original_error:
            message += f": {str(original_error)}"
        super().__init__(message)
        self.encoded_url = encoded_url
        self.original_error = original_error


# Funções auxiliares para criar exceções com contexto


def create_invalid_url_error(url: str) -> InvalidURLError:
    """Cria erro de URL inválida com formato esperado"""
    expected = "https://www.weekseries.info/series/[serie]/temporada-[numero]/episodio-[numero]"
    return InvalidURLError(url, expected)


def create_parsing_error(url: str, content_length: int = None) -> ParsingError:
    """Cria erro de parsing com detalhes do conteúdo"""
    details = None
    if content_length is not None:
        if content_length == 0:
            details = "página vazia"
        elif content_length < 1000:
            details = "conteúdo muito pequeno"
        else:
            details = f"conteúdo de {content_length} caracteres processado"

    return ParsingError(url, details)


def create_network_error(url: str, original_error: Exception) -> NetworkError:
    """Cria erro de rede com contexto da exceção original"""
    return NetworkError(url, original_error)
