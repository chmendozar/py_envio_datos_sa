"""
Cliente HTTP mejorado con configuraciones avanzadas para web scraping.
Incluye retry logic, connection pooling, rate limiting y mejor manejo de errores.
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import random
import time
import logging
from typing import Optional, Dict, Any, List
import urllib3
from contextlib import contextmanager

# Deshabilitar warnings de SSL para desarrollo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class RateLimiter:
    """Controlador de rate limiting para evitar ser bloqueado."""
    
    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
    
    def wait(self):
        """Espera un tiempo aleatorio entre peticiones."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            sleep_time = random.uniform(self.min_delay, self.max_delay)
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

class AdvancedHTTPClient:
    """
    Cliente HTTP avanzado con múltiples mejoras:
    - Connection pooling
    - Retry logic con backoff exponencial
    - Rate limiting
    - Rotación de User-Agents
    - Headers dinámicos
    - Manejo de proxies (opcional)
    """
    
    def __init__(self, 
                 max_retries: int = 3,
                 timeout: int = 15,
                 pool_connections: int = 10,
                 pool_maxsize: int = 20,
                 rate_limit_min: float = 1.0,
                 rate_limit_max: float = 3.0,
                 verify_ssl: bool = True):
        
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.rate_limiter = RateLimiter(rate_limit_min, rate_limit_max)
        
        # Configurar sesión
        self.session = requests.Session()
        
        # Configurar retry strategy con backoff exponencial
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504, 520, 521, 522, 523, 524],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=2,  # Backoff exponencial: 1s, 2s, 4s, 8s...
            respect_retry_after_header=True,
            raise_on_status=False  # No lanzar excepción automáticamente
        )
        
        # Configurar adapter con connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            pool_block=False
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Lista de User-Agents para rotación
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0"
        ]
        
        # Lista de idiomas para rotación
        self.languages = [
            "es-PE,es;q=0.9,en;q=0.8,en-US;q=0.7",
            "en-US,en;q=0.9,es;q=0.8",
            "es-ES,es;q=0.9,en;q=0.8",
            "en-GB,en;q=0.9,es;q=0.8",
            "es-MX,es;q=0.9,en;q=0.8"
        ]
        
        # Configurar headers por defecto
        self.session.headers.update(self._get_default_headers())
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Genera headers por defecto más robustos."""
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": random.choice(self.languages),
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"'
        }
    
    def get_random_headers(self) -> Dict[str, str]:
        """Genera headers aleatorios para parecer más natural."""
        headers = self._get_default_headers()
        
        # Rotar User-Agent
        headers["User-Agent"] = random.choice(self.user_agents)
        
        # Rotar Accept-Language
        headers["Accept-Language"] = random.choice(self.languages)
        
        # Agregar headers adicionales aleatorios
        if random.random() > 0.5:
            headers["Referer"] = "https://www.google.com/"
        
        return headers
    
    def make_request(self, 
                    url: str, 
                    timeout: Optional[int] = None,
                    headers: Optional[Dict[str, str]] = None,
                    verify_ssl: Optional[bool] = None,
                    allow_redirects: bool = True,
                    max_redirects: int = 5) -> Optional[requests.Response]:
        """
        Realiza una petición HTTP con todas las mejoras implementadas.
        
        Args:
            url: URL a consultar
            timeout: Timeout personalizado
            headers: Headers personalizados
            verify_ssl: Si verificar SSL
            allow_redirects: Si permitir redirecciones
            max_redirects: Máximo número de redirecciones
            
        Returns:
            Response object o None si hay error
        """
        # Rate limiting
        self.rate_limiter.wait()
        
        try:
            # Usar timeout personalizado o el por defecto
            request_timeout = timeout or self.timeout
            
            # Usar headers personalizados o aleatorios
            request_headers = headers or self.get_random_headers()
            
            # Usar verify_ssl personalizado o el por defecto
            request_verify = verify_ssl if verify_ssl is not None else self.verify_ssl
            
            logger.info(f"Realizando petición a: {url}")
            logger.info(f"Timeout: {request_timeout}s, Headers: {len(request_headers)}")
            
            response = self.session.get(
                url,
                headers=request_headers,
                timeout=request_timeout,
                verify=request_verify,
                allow_redirects=allow_redirects,
                stream=False  # Para mejor manejo de memoria
            )
            
            # Log de información de la respuesta
            logger.info(f"Respuesta recibida: {response.status_code} - {len(response.content)} bytes")
            logger.info(f"Headers de respuesta: {dict(response.headers)}")
            
            # Verificar si la respuesta es exitosa
            if response.status_code >= 400:
                logger.warning(f"Error HTTP {response.status_code} en {url}")
                return None
            
            # Convertir el contenido de bytes a texto
            try:
                # Intentar detectar la codificación automáticamente
                encoding = response.apparent_encoding
                response.encoding = encoding
                response.text  # Forzar decodificación
                logger.info(f"Codificación detectada: {encoding}")
            except (UnicodeDecodeError, AttributeError):
                # Intentar codificaciones comunes en orden
                for enc in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        response.encoding = enc
                        response.text  # Forzar decodificación
                        logger.info(f"Decodificado exitosamente con {enc}")
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    logger.warning("No se pudo decodificar el contenido con ninguna codificación")
                    response.encoding = 'utf-8'  # Usar UTF-8 por defecto
            
            return response
            
        except requests.exceptions.Timeout as e:
            logger.warning(f"Timeout en petición a {url}: {e}")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Error de conexión a {url}: {e}")
            return None
        except requests.exceptions.TooManyRedirects as e:
            logger.warning(f"Demasiadas redirecciones en {url}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error de petición a {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado en petición a {url}: {e}")
            return None
    
    @contextmanager
    def session_context(self):
        """Context manager para manejar la sesión HTTP."""
        try:
            yield self
        finally:
            self.close()
    
    def close(self):
        """Cierra la sesión HTTP."""
        try:
            self.session.close()
        except Exception as e:
            logger.warning(f"Error al cerrar sesión HTTP: {e}")
    
    def get_session_info(self) -> Dict[str, Any]:
        """Obtiene información de la sesión HTTP."""
        return {
            "pool_connections": self.session.adapters['http://'].poolmanager.connection_pool_kw.get('maxsize', 0),
            "pool_maxsize": self.session.adapters['http://'].poolmanager.connection_pool_kw.get('maxsize', 0),
            "timeout": self.timeout,
            "verify_ssl": self.verify_ssl
        }

# Instancia global del cliente HTTP avanzado
advanced_http_client = AdvancedHTTPClient()

def get_http_client() -> AdvancedHTTPClient:
    """Obtiene la instancia global del cliente HTTP."""
    return advanced_http_client

def create_http_client(**kwargs) -> AdvancedHTTPClient:
    """Crea una nueva instancia del cliente HTTP con configuración personalizada."""
    return AdvancedHTTPClient(**kwargs) 