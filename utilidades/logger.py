import logging
import sys
from pathlib import Path

def init_logger(nivel=logging.INFO):
    # Crear el logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Evitar agregar múltiples handlers
    if not logger.hasHandlers():

        # Crear un handler para stdout (INFO y DEBUG)
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        
        # Crear un handler para stderr (WARNING, ERROR, CRITICAL)
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.WARNING)

        # Formateador de logs
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(name)s] [%(levelname)s] -> %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        stdout_handler.setFormatter(formatter)
        stderr_handler.setFormatter(formatter)

        # Agregar handlers al logger
        logger.addHandler(stdout_handler)
        logger.addHandler(stderr_handler)

    return logger