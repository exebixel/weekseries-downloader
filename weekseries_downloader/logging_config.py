"""
Configuração de logging para o weekseries downloader
"""

import logging
import logging.config
import os
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_file: str = None) -> None:
    """
    Configura o sistema de logging
    
    Args:
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Caminho para arquivo de log (opcional)
    """
    
    # Cria diretório de logs se necessário
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configuração base
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'simple',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            'weekseries_downloader': {
                'level': log_level,
                'handlers': ['console'],
                'propagate': False
            }
        },
        'root': {
            'level': log_level,
            'handlers': ['console']
        }
    }
    
    # Adiciona handler de arquivo se especificado
    if log_file:
        config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': log_level,
            'formatter': 'detailed',
            'filename': log_file,
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf-8'
        }
        
        # Adiciona handler de arquivo aos loggers
        config['loggers']['weekseries_downloader']['handlers'].append('file')
        config['root']['handlers'].append('file')
    
    # Aplica configuração
    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """
    Obtém logger configurado
    
    Args:
        name: Nome do logger (geralmente __name__)
        
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)


def setup_from_config_file(config_file: str = "logging.conf") -> None:
    """
    Configura logging a partir de arquivo de configuração
    
    Args:
        config_file: Caminho para arquivo de configuração
    """
    if os.path.exists(config_file):
        # Cria diretório de logs se necessário
        os.makedirs('logs', exist_ok=True)
        logging.config.fileConfig(config_file, disable_existing_loggers=False)
    else:
        # Fallback para configuração padrão
        setup_default_logging()


def setup_default_logging() -> None:
    """Configura logging padrão baseado em variáveis de ambiente"""
    
    # Obtém configurações de variáveis de ambiente
    log_level = os.getenv('WEEKSERIES_LOG_LEVEL', 'INFO').upper()
    log_file = os.getenv('WEEKSERIES_LOG_FILE')
    
    # Valida nível de log
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if log_level not in valid_levels:
        log_level = 'INFO'
    
    setup_logging(log_level, log_file)


# Configuração automática na importação
# Tenta usar arquivo de configuração, senão usa configuração padrão
setup_from_config_file()