import os
import sys
import time
import logging
from config.config import cargar_configuracion
from utilidades.logger import init_logger

# Configuracionn del logger
logger = logging.getLogger("Util - Planificador")

class Planificador:
    def __init__(self, fotofull, fotodelta):
        """
        Inicializa el remitente de correos electronicos.

        :param fotofull: Ejecutar bot de fotofull.
        :param fotodelta: Ejecutar bot de fotofull.
        :param inicioFotofull: Inicio del servicio Fotofull.
        :param inicioFotodelta: Inicio del servicio Fotodelta
        :param finFotodelta: Fin del servicio Fotodelta
        """
        self.fotofull = fotofull
        self.fotodelta = fotodelta

    def run(self):
        try:
            # Funcion para cargar el archivo de configuración
            cfg = cargar_configuracion()

            # Inicializar logger
            init_logger(nivel=logging.INFO)
            logger.info("Inicio del proceso ...")

            # Inicializar el planificador
            while True:
                current_time = time.strftime("%H:%M")
                if current_time == cfg["horario"]["inicioFotofull"]:
                    logger.info("Iniciando Fotofull...")
                    self.fotofull()
                elif cfg["horario"]["inicioFotodelta"] <= current_time <= cfg["horario"]["finFotodelta"] and current_time.endswith(":00"):
                    logger.info("Iniciando Fotodelta...")
                    self.fotodelta()
                time.sleep(cfg["horario"]["tiempodelay"]) # por defecto esta establecido en 1hr (3600 seg)
        except Exception as e:
            logger.error(f"Error al ejecutar: {e}")