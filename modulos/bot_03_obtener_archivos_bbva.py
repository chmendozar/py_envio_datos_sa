import logging
import configparser
import polars as pl
from pathlib import Path
from datetime import datetime
from utilidades.excepciones import BusinessException

logger = logging.getLogger("Bot 03 - Obtener Archivos BBVA")

def bot_run(cfg, mensaje="Bot 03 - Obtener Archivos BBVA"):
    resultado = False
    try:
        logger.info("Iniciando ejecución del bot_run.")
    except BusinessException as be:
        logger.error(f"Error de negocio en bot_run: {be}")
        mensaje = f"Error de negocio: {be}"
    except Exception as e:
        logger.error(f"Error inesperado en bot_run: {e}")
        mensaje = f"Error inesperado: {e}"
    finally:
        logger.info("Fin del bot: %s", mensaje)
        return resultado, mensaje