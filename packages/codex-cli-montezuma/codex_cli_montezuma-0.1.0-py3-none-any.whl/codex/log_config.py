import logging
import sys
import os

LOG_FORMAT = "[%(asctime)s] %(levelname)s [%(name)s]: %(message)s"
LOG_LEVEL = os.environ.get("CODEX_LOG_LEVEL", "WARNING")

def setup_logging(level: str = None, log_format: str = LOG_FORMAT, log_file: str = None) -> None:
    """
    Configura logging global para o projeto Codex CLI.
    Por padrão, loga para o console. Se log_file for fornecido, loga também em arquivo.
    O nível de log pode ser definido por argumento, variável de ambiente CODEX_LOG_LEVEL, ou flag --verbose.
    """
    if level is None:
        level = LOG_LEVEL
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.WARNING),
        format=log_format,
        handlers=handlers,
        force=True
    )

# Exemplo de uso:
# from codex.log_config import setup_logging
# setup_logging(level="DEBUG", log_file="codex.log")
