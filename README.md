# WeekSeries Downloader

Script para baixar vídeos do WeekSeries usando Python puro (sem dependência do ffmpeg para download, apenas para conversão opcional).

## Características

- ✅ Download de streams HLS (m3u8) usando apenas Python
- 🎬 Conversão automática para MP4 (se ffmpeg estiver disponível)
- 📱 Interface de linha de comando moderna com Click
- 🔄 Suporte a playlists master (múltiplas qualidades)
- 🧹 Limpeza automática de arquivos temporários
- ⚡ Progresso em tempo real
- 🛡️ Headers apropriados para evitar bloqueios

## Instalação

### Configuração do Poetry

Para usar ambientes virtuais locais (recomendado):

```bash
# Configurar Poetry para criar .venv na pasta do projeto
poetry config virtualenvs.in-project true

# Verificar configurações
poetry config --list | grep virtualenvs
```

### Usando Poetry (Recomendado)

```bash
# Clone o repositório
git clone <url-do-repo>
cd weekseries-downloader

# Configure Poetry para usar .venv local (se necessário)
poetry config virtualenvs.in-project true

# Instale as dependências
poetry install

# Ative o ambiente virtual
poetry shell
```

### Usando pip

```bash
# Clone o repositório
git clone <url-do-repo>
cd weekseries-downloader

# Instale o pacote
pip install .
```

## Uso

Após a instalação, você pode usar o comando `weekseries-dl`:

### Exemplos

```bash
# Baixar usando URL base64 codificada
weekseries-dl --encoded "aHR0cHM6Ly9zZXJpZXMudmlkbWFuaWl4LnNob3AvVC90aGUtZ29vZC1kb2N0b3IvMDItdGVtcG9yYWRhLzE2L3N0cmVhbS5tM3U4"

# Baixar usando URL direta
weekseries-dl --url "https://series.vidmaniix.shop/T/the-good-doctor/02-temporada/16/stream.m3u8"

# Especificar arquivo de saída
weekseries-dl --url "..." --output "meu-video.mp4"

# Com referer específico
weekseries-dl --url "..." --referer "https://www.weekseries.info/series/the-good-doctor/temporada-2/episodio-16"

# Manter apenas arquivo .ts (sem conversão para MP4)
weekseries-dl --url "..." --no-convert

# Ver ajuda completa
weekseries-dl --help
```

### Opções disponíveis

- `--url, -u`: URL direta do stream m3u8
- `--encoded, -e`: URL do stream codificada em base64
- `--output, -o`: Nome do arquivo de saída (padrão: video.mp4)
- `--referer, -r`: URL da página de referência
- `--no-convert`: Não converter para MP4, manter apenas .ts
- `--help`: Mostrar ajuda
- `--version`: Mostrar versão

## Dependências Opcionais

### FFmpeg (Para conversão MP4)

O script pode baixar vídeos sem ffmpeg, mas para converter automaticamente de .ts para .mp4:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# Baixe de https://ffmpeg.org/download.html
```

## Desenvolvimento

### Configuração do ambiente de desenvolvimento

```bash
# Clone o repositório
git clone <url-do-repo>
cd weekseries-downloader

# Configure Poetry para usar .venv local (opcional, se não estiver configurado)
poetry config virtualenvs.in-project true

# Instale dependências de desenvolvimento
poetry install

# Ative o ambiente virtual
poetry shell

# Execute testes
pytest

# Formatação de código
black weekseries_downloader/

# Linting
flake8 weekseries_downloader/
```

### Estrutura do projeto

```
weekseries-downloader/
├── weekseries_downloader/
│   ├── __init__.py          # Informações do pacote
│   ├── cli.py               # Interface de linha de comando
│   ├── downloader.py        # Lógica principal de download
│   ├── converter.py         # Conversão de vídeos
│   └── utils.py             # Utilitários diversos
├── pyproject.toml           # Configuração do Poetry
├── README.md                # Este arquivo
└── download_video_pure.py   # Script original (mantido para compatibilidade)
```

## Como funciona

1. **Download da playlist**: Baixa o arquivo m3u8 que contém a lista de segmentos
2. **Parsing**: Extrai URLs dos segmentos de vídeo
3. **Download dos segmentos**: Baixa cada segmento .ts individualmente
4. **Concatenação**: Junta todos os segmentos em um único arquivo .ts
5. **Conversão (opcional)**: Converte para .mp4 usando ffmpeg se disponível

## Licença

MIT License - veja o arquivo LICENSE para detalhes.

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Aviso Legal

Este script é apenas para fins educacionais. Certifique-se de ter permissão para baixar o conteúdo e respeite os termos de uso dos sites.