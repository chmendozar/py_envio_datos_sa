import logging
import variables_globales as vg
from utilidades.limpieza import cerrarProcesos as Limpieza
from modulos.bot_00_configuracion import bot_run as Bot_00_Configuracion
from modulos.bot_01_super_admin import bot_run as Bot_01_SuperAdmin
from modulos.bot_02_procesar_reporte import bot_run as Bot_02_ProcesarReporte
from utilidades.notificaiones_whook import WebhookNotifier

from datetime import datetime
import traceback
import platform
import os
import psutil

logger = logging.getLogger("Main - Orquestador")


def obtener_info_sistema():
    """
    Recopila información del sistema para diagnóstico.

    Returns:
        dict: Información básica del sistema
    """
    try:
        info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "processor": platform.processor(),
            "memory": f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
            "cpu_count": os.cpu_count(),
            "cpu_usage": f"{psutil.cpu_percent()}%",
            "available_memory": f"{round(psutil.virtual_memory().available / (1024**3), 2)} GB"
        }
        return info
    except Exception as e:
        logger.warning(f"No se pudo obtener información completa del sistema: {e}")
        return {"error": str(e)}


def main():
    inicio = datetime.now()
    
    # Limpieza de ambiente
    lista_procesos = ["chrome.exe", "firefox.exe"]
    Limpieza(lista_procesos)

    logger.info(f"==================== INICIO DE ORQUESTACIÓN ====================")
    logger.info(f"Inicio de orquestación - {inicio.strftime('%Y-%m-%d %H:%M:%S')}")

    # Recopilar información del sistema
    info_sistema = obtener_info_sistema()
    logger.info(f"Información del sistema: {info_sistema}")

    try:
        # Configuración del bot
        logger.info("Cargando configuración del sistema...")
        cfg = Bot_00_Configuracion()
        if not cfg:
            logger.error("Error al cargar la configuración. Abortando proceso.")
            vg.system_exception = True
            return

        logger.info(f"Configuración cargada exitosamente. Secciones disponibles: {', '.join(cfg.keys())}")

       

        # Notificación de inicio
        #notificaion.send_notification("Inicio del proceso tipo de cambio PayPal")

        # Ejecución de los bots
        for bot_name, bot_function in [
            ("Bot 01 - Obtener TC bloomberg", Bot_01_SuperAdmin),
            ("Bot 02 - Procesar Reporte", Bot_02_ProcesarReporte),
        ]:
            logger.info(f"==================== INICIANDO {bot_name} ====================")
            resultado, mensaje = bot_function(cfg)
                
        
        # Verificar si hay excepciones de negocio o sistema
        if vg.business_exception:
            logger.info("Enviando Notificación por Error de Negocio...")
            return

        if vg.system_exception:
            logger.info("Enviando Notificación por Error de Sistema...")
            return

    except Exception as e:
        logger.error(f"Error en main: {e}")
        logger.error(traceback.format_exc())

    finally:
        # Calcular tiempo total de ejecución
        fin = datetime.now()
        tiempo_total = fin - inicio
        logger.info(f"==================== FIN DE ORQUESTACIÓN ====================")
        logger.info(f"Fin de orquestación - {fin.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Tiempo total de ejecución: {tiempo_total}")
        
        # Notificación de fin
        #notificaion.send_notification(f"Fin del proceso de orquestación. Tiempo total de ejecución: {tiempo_total}")
        logger.info("Fin del proceso ...")


if __name__ == "__main__":
    main()