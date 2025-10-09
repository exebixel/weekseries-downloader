# Design Document

## Overview

Este documento descreve o design para implementar uma estrutura de testes abrangente para o projeto weekseries_downloader. O sistema de testes será baseado em pytest e seguirá princípios de testes unitários isolados, usando mocks para dependências externas e fixtures para configuração de testes.

A arquitetura de testes espelhará a estrutura do projeto principal, com cada módulo tendo seu arquivo de teste correspondente. O design prioriza isolamento, facilidade de manutenção e cobertura abrangente.

## Architecture

### Test Structure
```
tests/
├── __init__.py
├── conftest.py                    # Fixtures compartilhadas
├── test_models.py                 # Testes para models.py
├── test_utils.py                  # Testes para utils.py
├── test_url_detector.py           # Testes para url_detector.py
├── test_filename_generator.py     # Testes para filename_generator.py
├── test_cache.py                  # Testes para cache.py
├── test_exceptions.py             # Testes para exceptions.py
├── test_extractor.py              # Testes para extractor.py
├── test_downloader.py             # Testes para downloader.py
├── test_converter.py              # Testes para converter.py
├── test_cli.py                    # Testes para cli.py
└── test_logging_config.py         # Testes para logging_config.py
```

### Testing Principles

1. **Isolation**: Cada teste é independente e não afeta outros testes
2. **Mocking**: Dependências externas (HTTP, filesystem, subprocess) são mockadas
3. **Fixtures**: Dados de teste reutilizáveis são definidos como fixtures
4. **Coverage**: Todos os caminhos de código principais são testados
5. **Edge Cases**: Casos extremos e condições de erro são testados

## Components and Interfaces

### 1. Test Configuration (conftest.py)

**Purpose**: Configuração central de fixtures e configurações de teste

**Key Components**:
- Fixtures para objetos de dados comuns (EpisodeInfo, ExtractionResult, etc.)
- Mocks para dependências externas
- Configuração de logging para testes
- Fixtures para URLs de exemplo

### 2. Models Testing (test_models.py)

**Purpose**: Testa classes de dados e suas propriedades

**Test Categories**:
- **EpisodeInfo Tests**:
  - Criação de instâncias válidas
  - Propriedade `filename_safe_name` com caracteres especiais
  - Método `__str__` para representação
  - Validação de tipos de dados

- **ExtractionResult Tests**:
  - Estados de sucesso e erro
  - Propriedades booleanas (`is_error`, `has_stream_url`)
  - Comportamento em contextos booleanos
  - Validação de campos opcionais

- **DownloadConfig Tests**:
  - Configuração válida e inválida
  - Propriedade `has_referer`
  - Validação de URLs

### 3. Utils Testing (test_utils.py)

**Purpose**: Testa funções utilitárias puras e com dependências

**Test Categories**:
- **decode_base64_url Tests**:
  - URLs base64 válidas
  - Strings inválidas ou corrompidas
  - Casos extremos (string vazia, None)

- **sanitize_filename Tests**:
  - Caracteres especiais do sistema de arquivos
  - Strings Unicode
  - Nomes muito longos

- **check_ffmpeg Tests** (com mock):
  - ffmpeg instalado e funcionando
  - ffmpeg não instalado
  - Erro na execução

- **create_request Tests**:
  - Headers padrão
  - Headers com referer customizado
  - Validação de User-Agent

### 4. URL Detector Testing (test_url_detector.py)

**Purpose**: Testa detecção e validação de URLs

**Test Categories**:
- **detect_url_type Tests**:
  - URLs do weekseries.info válidas
  - URLs de streaming direto (.m3u8)
  - Strings base64 válidas
  - URLs inválidas ou não suportadas

- **validate_weekseries_url Tests**:
  - Padrões válidos de URL
  - URLs malformadas
  - Protocolos diferentes (http/https)

- **extract_episode_info Tests**:
  - Extração de informações válidas
  - URLs que não seguem o padrão
  - Validação de números de temporada/episódio

### 5. Cache Testing (test_cache.py)

**Purpose**: Testa sistema de cache em memória

**Test Categories**:
- **SimpleCache Tests**:
  - Operações básicas (get/set)
  - Expiração de entradas (TTL)
  - Limpeza de cache
  - Estatísticas de cache

- **Global Cache Functions Tests**:
  - `get_cached_stream_url` e `cache_stream_url`
  - `clear_url_cache` e `cleanup_expired_urls`
  - `get_cache_stats`

### 6. Exceptions Testing (test_exceptions.py)

**Purpose**: Testa exceções customizadas

**Test Categories**:
- **Exception Creation Tests**:
  - Criação com mensagens customizadas
  - Herança correta de Exception
  - Propriedades específicas (url, original_error)

- **Helper Functions Tests**:
  - `create_invalid_url_error`
  - `create_parsing_error`
  - `create_network_error`

### 7. Extractor Testing (test_extractor.py)

**Purpose**: Testa extração de URLs com dependency injection

**Test Categories**:
- **extract_stream_url Tests** (com mocks):
  - Extração bem-sucedida
  - Falhas de rede
  - Falhas de parsing
  - Cache hit/miss

- **Dependency Injection Tests**:
  - HttpClient mock
  - HtmlParser mock
  - Base64Decoder mock

### 8. Downloader Testing (test_downloader.py)

**Purpose**: Testa download de vídeos HLS

**Test Categories**:
- **download_m3u8_playlist Tests** (com mocks):
  - Download bem-sucedido
  - Erros de rede
  - Timeouts

- **parse_m3u8 Tests**:
  - Parsing de playlist válida
  - URLs relativas e absolutas
  - Playlists malformadas

### 9. Converter Testing (test_converter.py)

**Purpose**: Testa conversão de vídeos

**Test Categories**:
- **convert_to_mp4 Tests** (com mocks):
  - Conversão bem-sucedida
  - Falhas do ffmpeg
  - Arquivos inexistentes

### 10. CLI Testing (test_cli.py)

**Purpose**: Testa interface de linha de comando

**Test Categories**:
- **process_url_input Tests**:
  - Diferentes tipos de URL
  - URLs codificadas
  - Casos de erro

- **create_dependencies Tests**:
  - Criação de dependências válidas

## Data Models

### Test Data Fixtures

```python
# Exemplo de fixtures em conftest.py
@pytest.fixture
def sample_episode_info():
    return EpisodeInfo(
        series_name="the-good-doctor",
        season=1,
        episode=3,
        original_url="https://www.weekseries.info/series/the-good-doctor/temporada-1/episodio-03"
    )

@pytest.fixture
def sample_extraction_result():
    return ExtractionResult(
        success=True,
        stream_url="https://example.com/stream.m3u8",
        referer_url="https://www.weekseries.info/"
    )
```

### Mock Configurations

```python
# Exemplo de mocks para HTTP requests
@pytest.fixture
def mock_http_client():
    with patch('urllib.request.urlopen') as mock:
        mock.return_value.__enter__.return_value.read.return_value = b'<html>content</html>'
        yield mock
```

## Error Handling

### Test Error Scenarios

1. **Network Errors**: Simular falhas de conexão, timeouts
2. **Parsing Errors**: HTML malformado, padrões não encontrados
3. **File System Errors**: Permissões, espaço em disco
4. **Invalid Input**: URLs malformadas, dados corrompidos

### Exception Testing Strategy

- Verificar que exceções corretas são lançadas
- Validar mensagens de erro
- Testar propagação de exceções
- Verificar cleanup em casos de erro

## Testing Strategy

### Unit Test Categories

1. **Pure Functions**: Testadas diretamente sem mocks
2. **Functions with I/O**: Testadas com mocks apropriados
3. **Classes**: Testadas com instâncias isoladas
4. **Integration Points**: Testados com mocks de dependências

### Mock Strategy

- **HTTP Requests**: Mock `urllib.request.urlopen`
- **File System**: Mock `pathlib.Path` operations
- **Subprocess**: Mock `subprocess.run`
- **Time**: Mock `time.time` para testes de cache

### Coverage Goals

- **Line Coverage**: Mínimo 90%
- **Branch Coverage**: Mínimo 85%
- **Function Coverage**: 100%

### Test Execution

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=weekseries_downloader --cov-report=html

# Executar testes específicos
pytest tests/test_models.py

# Executar com verbose
pytest -v
```