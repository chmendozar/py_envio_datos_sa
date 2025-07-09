import logging
import os
from pathlib import Path
from config.config import cargar_configuracion
from utilidades.logger import init_logger
from dotenv import load_dotenv

# Configuracion del logger
logger = logging.getLogger("Bot 00 - Configurador")

load_dotenv()

def bot_run():

    try:
        # Funcion para cargar el archivo de configuración
        cfg = cargar_configuracion()
        # Cargar variables de entorno desde .env si existe
        env_path = Path('.env')
        if not env_path.exists():            
            logger.error("No se encontró el archivo .env")
            raise Exception("No se encontró el archivo .env")
        # Se crea la carpeta de input si no existe
        # Agregar env_vars desde .env al cfg
        if env_path.exists():
            cfg["env_vars"] = {
                "super_admin_user": os.getenv("SUPER_ADMIN_USER"),
                "super_admin_pwd": os.getenv("SUPER_ADMIN_PWD"),
                "webhook_rpa_url": os.getenv("WEBHOOK_RPA_URL"),
                "bbva": {
                    "code": os.getenv("BBVA_CODE"), 
                    "user": os.getenv("BBVA_USER"),
                    "password": os.getenv("BBVA_PASSWORD")
                }
            }

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