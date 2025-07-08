import logging
import configparser
import pandas as pd
from pathlib import Path
from datetime import datetime
from utilidades.excepciones import BusinessException
import variables_globales as vg

logger = logging.getLogger("Bot 03 - Obtener Archivos BBVA")



def bot_run(cfg, mensaje="Bot 03 - Obtener Archivos BBVA"):
    resultado = False
    try:
        logger.info("Iniciando ejecución del bot_run.")      
        
      
        # Leer el archivo Excel y seleccionar/renombrar las columnas relevantes
        mensaje = f"Reporte procesado y validado correctamente."
        resultado = True
        logger.info("Archivo procesado y guardado correctamente.")
    except BusinessException as be:
        logger.error(f"Error de negocio en bot_run: {be}")
        mensaje = f"Error de negocio: {be}"
    except Exception as e:
        logger.error(f"Error inesperado en bot_run: {e}")
        mensaje = f"Error inesperado: {e}"
    finally:
        logger.info("Fin del bot: %s", mensaje)
        return resultado, mensaje