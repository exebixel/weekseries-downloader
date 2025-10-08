# Sistema de Logging

O WeekSeries Downloader utiliza o módulo `logging` padrão do Python para registrar eventos e erros.

## Configuração

### Arquivo de Configuração

O sistema usa o arquivo `logging.conf` na raiz do projeto. Este arquivo define:

- **Loggers**: `root` e `weekseries_downloader`
- **Handlers**: Console e arquivo rotativo
- **Formatters**: Simples (console) e detalhado (arquivo)

### Variáveis de Ambiente

Você pode configurar o logging através de variáveis de ambiente:

```bash
# Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
export WEEKSERIES_LOG_LEVEL=DEBUG

# Arquivo de log personalizado
export WEEKSERIES_LOG_FILE=/path/to/custom.log
```

## Níveis de Log

- **DEBUG**: Informações detalhadas para debugging
- **INFO**: Informações gerais sobre o progresso
- **WARNING**: Avisos sobre situações não críticas
- **ERROR**: Erros que impedem operações específicas
- **CRITICAL**: Erros críticos que podem parar o programa

## Arquivos de Log

### Console
- Formato simples: `LEVEL - MESSAGE`
- Mostra apenas INFO e acima por padrão

### Arquivo
- Local: `logs/weekseries-downloader.log`
- Formato detalhado com timestamp, módulo e linha
- Rotação automática (10MB, 5 backups)
- Inclui DEBUG e acima

## Exemplos de Uso

### Desenvolvimento
```bash
# Logs detalhados no console
export WEEKSERIES_LOG_LEVEL=DEBUG
weekseries-dl --url "..."
```

### Produção
```bash
# Apenas erros no console, tudo no arquivo
export WEEKSERIES_LOG_LEVEL=ERROR
weekseries-dl --url "..."
```

### Log Personalizado
```bash
# Arquivo de log específico
export WEEKSERIES_LOG_FILE=/var/log/weekseries.log
weekseries-dl --url "..."
```

## Estrutura dos Logs

### Console (INFO)
```
INFO - Baixando playlist m3u8...
INFO - Total de segmentos: 150
INFO - Progresso: 15/150 (10.0%)
```

### Arquivo (DEBUG)
```
2024-01-15 14:30:15 - weekseries_downloader.extractor - INFO - extractor:extract_stream_url:45 - Extraindo URL de streaming...
2024-01-15 14:30:16 - weekseries_downloader.downloader - INFO - downloader:download_hls_video:108 - URL do stream: https://example.com/stream.m3u8
```

## Personalização

Para personalizar o logging, edite o arquivo `logging.conf` ou crie sua própria configuração:

```python
from weekseries_downloader.logging_config import setup_logging

# Configuração personalizada
setup_logging(log_level="DEBUG", log_file="meu_log.log")
```