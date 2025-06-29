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
        input_path = Path(cfg["rutas"]["ruta_input"])
        if not input_path.exists():
            input_path.mkdir(parents=True)
        else:
            # Limpiar todos los archivos y carpetas dentro de input
            for item in input_path.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    for subitem in item.rglob("*"):
                        if subitem.is_file():
                            subitem.unlink()
                        elif subitem.is_dir():
                            subitem.rmdir()
                    item.rmdir()

        # Se crea la carpeta de output si no existe
        output_path = Path(cfg["rutas"]["ruta_output"])
        if not output_path.exists():
            output_path.mkdir(parents=True)

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