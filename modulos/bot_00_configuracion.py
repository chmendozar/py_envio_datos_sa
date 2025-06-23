import logging
from pathlib import Path
from config.config import cargar_configuracion
from utilidades.logger import init_logger

# Configuracion del logger
logger = logging.getLogger("Bot 00 - Configurador")

def bot_run():

    try:
        # Funcion para cargar el archivo de configuración
        cfg = cargar_configuracion()

        # Se crea la carpeta de input si no existe
        if not Path(cfg["rutas"]["ruta_input"]).exists():
            Path(cfg["rutas"]["ruta_input"]).mkdir(parents=True)

        # Se crea la carpeta de output si no existe
        if not Path(cfg["rutas"]["ruta_output"]).exists():
            Path(cfg["rutas"]["ruta_output"]).mkdir(parents=True)

        # Inicializar logger
        init_logger(nivel=logging.INFO)
        logger.info("Inicio del proceso ...")

        # Imprimir configuracion
        logger.info(f"Configuracion cargada")
        logger.info(f"Ruta de input: {cfg['rutas']['ruta_input']}")
        logger.info(f"Ruta de output: {cfg['rutas']['ruta_output']}")

        return cfg
    
    except Exception as e:
        logger.error(f"Error en bot_run: {e}")
        return None
    finally:
        logger.info("Fin del proceso ...")