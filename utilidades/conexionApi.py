
import requests
import logging
from requests.auth import HTTPBasicAuth

# Configuracionn del logger
logger = logging.getLogger("Utils - ConexionApi")

class ConexionApi:
    def __init__(self, url_api, clave_api=None, auth_tipo=None, auth_credenciales=None):
        """
        Inicializa el cliente de la API.
        
        :param url_api: La URL base de la API de Rappi.
        :param clave_api: La clave de la API para autenticación.
        """
        self.url_api = url_api
        self.clave_api = clave_api
        self.encabezados = {
            "Content-Type": "application/json",
        }
        self.auth = None

        # Agregar la clave de API al encabezado si está disponible
        if self.clave_api:
            self.encabezados["API_KEY"] = self.clave_api

        # Configuración de autenticación
        if auth_tipo == "Bearer" and auth_credenciales:
            self.encabezados["Authorization"] = f"Bearer {auth_credenciales}"
        elif auth_tipo == "Basic" and isinstance(auth_credenciales, tuple):
            self.auth = HTTPBasicAuth(*auth_credenciales)

    def enviar_post(self, endpoint=None, datos=None):
        """
        Envía una petición POST a la API.

        :param endpoint: El endpoint al que se enviará la petición (relativo a la URL base).
        :param datos: El payload JSON que contiene los registros (opcional).
        :return: La respuesta JSON si la petición es exitosa.
        """
        try:
            url_completa = self._build_url(endpoint)
            respuesta = requests.post(
                url_completa, headers=self.encabezados, json=datos, auth=self.auth
            )
            respuesta.raise_for_status()  # Lanza un error HTTP para respuestas 4xx y 5xx
            logging.info(f"POST exitoso a {url_completa}. Respuesta: {respuesta.json()}")
            return respuesta.json(), respuesta.status_code
        except requests.exceptions.HTTPError as error_http:
            logging.error(f"Error HTTP en POST: {error_http}")
            raise
        except requests.exceptions.RequestException as error_peticion:
            logging.error(f"Error en la petición POST: {error_peticion}")
            raise

    def _build_url(self, endpoint=None):
        """
        Construye la URL completa combinando la URL base con el endpoint (si se proporciona).
        :param endpoint: El endpoint relativo (opcional).
        :return: La URL completa.
        """
        if endpoint:
            return f"{self.url_api}/{endpoint.lstrip('/')}"  # Combina base URL y endpoint
        return self.url_api  # Solo retorna la base URL si no hay endpoint

    def enviar_get(self, endpoint=None, parametros=None, datos=None):
        """
        Envía una petición GET a la API.

        :param endpoint: El endpoint al que se enviará la petición (relativo a la URL base).
        :param parametros: Diccionario opcional de parámetros de consulta (query params).
        :param datos: Cuerpo JSON opcional para incluir en la petición GET (no estándar, pero soportado si necesario).
        :return: La respuesta JSON si la petición es exitosa.
        """
        try:
            url_completa = self._build_url(endpoint)
            respuesta = requests.get(
                url_completa, headers=self.encabezados, params=parametros, json=datos, auth=self.auth
            )
            respuesta.raise_for_status()  # Lanza un error HTTP para respuestas 4xx y 5xx
            logging.info(f"GET exitoso a {url_completa}. Respuesta: {respuesta.json()}")
            return respuesta.json(), respuesta.status_code
        except requests.exceptions.HTTPError as error_http:
            logging.error(f"Error HTTP en GET: {error_http}")
            raise
        except requests.exceptions.RequestException as error_peticion:
            logging.error(f"Error en la petición GET: {error_peticion}")
            raise