import logging
import configparser
import requests
import os
from pathlib import Path
from utilidades.excepciones import BusinessException
from datetime import datetime

logger = logging.getLogger("Bot 01 - Super Admin")

def super_admin_login(cfg):
    username = cfg["env_vars"]["super_admin_user"]
    password = cfg["env_vars"]["super_admin_pwd"]
    
    # Leer URLs desde el archivo de configuración
    base_url = cfg["url"]["url_superadmin"]
    login_url = f"{base_url}{cfg['url'] ['url_login']}"

    # Crear una sesión para mantener las cookies
    session = requests.Session()

    # Datos del formulario de inicio de sesión
    login_data = {
        "usuario": username, 
        "password": password 
    }

    # Encabezados de la solicitud
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Realizar la solicitud POST para iniciar sesión
    login_response = session.post(login_url, data=login_data, headers=headers)

    # Verificar si el inicio de sesión fue exitoso
    if login_response.status_code == 200:
        login_result = login_response.json()
        if login_result.get("respuesta") == "00":
            logger.info(f"Inicio de sesión exitoso. Bienvenido {login_result.get('nombres')}!")
            return session
        else:
            raise BusinessException(f"Inicio de sesión fallido. Mensaje: {login_result.get('mensaje')}")
    else:
        raise BusinessException(f"Error en la solicitud de inicio de sesión: {login_response.status_code}")

def descargar_recaudo(cfg, session):
    base_url = cfg["url"]["url_superadmin"]
    fechas_recaudo = datetime.now().strftime("%d/%m/%Y%%20-%%20%d/%m/%Y")
    url_descarga = f"{base_url}{cfg['url']['url_recaudo_descarga']}{fechas_recaudo}"
    response = session.get(url_descarga)
    if response.status_code == 200:
        logger.info(f"Recaudo descargado correctamente")                
        input_path = os.path.join(cfg['rutas']['ruta_input'], 'recaudo.xls')
        with open(input_path, 'wb') as f:
            f.write(response.content)
        logger.info(f"Archivo guardado en: {input_path}")
        return input_path
    else:
        raise BusinessException(f"Error al descargar el recaudo: {response.status_code}")

def bot_run(cfg, mensaje="Bot 01 - Super Admin"):
    resultado = False
    try:
        # Leer configuración
        config = configparser.ConfigParser()
        config.read(cfg)
        session = super_admin_login(cfg)
        input_path = descargar_recaudo(cfg, session)
        if Path(input_path).exists():
            logger.info(f"Archivo recaudo descargado correctamente")
            mensaje = f"Archivo recaudo descargado correctamente"
            resultado = True
        else:
            logger.error(f"Error al descargar el recaudo")
            mensaje = f"Error al descargar el recaudo"

    except BusinessException as be:
        logger.error(f"Error de negocio en bot_run: {be}")
        mensaje = f"Error de negocio: {be}"
    except Exception as e:
        logger.error(f"Error inesperado en bot_run: {e}")
        mensaje = f"Error inesperado: {e}"
    finally:
        logger.info("Fin del bot: %s", mensaje)
        return resultado, mensaje