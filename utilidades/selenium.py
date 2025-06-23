import logging
import os
import tempfile
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

logger = logging.getLogger("Utils - Selenium")

class SeleniumHelper:
    def __init__(self, headless=True, profilename="default"):
        chrome_options = Options()
        
        # Lista de User-Agents reales para rotar
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        selected_user_agent = random.choice(user_agents)
        
        # Configuración del perfil
        try:
            profile_dir = os.path.join(tempfile.gettempdir(), f"chrome_profile_{profilename}")
            os.makedirs(profile_dir, exist_ok=True)
            chrome_options.add_argument(f"--user-data-dir={profile_dir}")
            logger.info(f"Using profile directory: {profile_dir}")
        except Exception as e:
            logger.warning(f"Could not create profile directory: {e}")
        
        # Configuración básica
        if headless:
            chrome_options.add_argument("--headless=new")  # Usar nuevo modo headless
        
        # Configuración anti-detección mejorada
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions-except")
        chrome_options.add_argument("--disable-plugins-discovery")
        chrome_options.add_argument(f"--user-agent={selected_user_agent}")
        
        # IMPORTANTE: NO deshabilitar JavaScript
        # chrome_options.add_argument("--disable-javascript")  # COMENTADO
        
        # Configuración experimental
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Preferencias mejoradas
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.default_content_setting_values.cookies": 1,
            "profile.block_third_party_cookies": False,
            "profile.default_content_setting_values.geolocation": 2,
            "profile.default_content_setting_values.media_stream": 2,
        }
        chrome_options.add_experimental_option("prefs", prefs)

        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), 
                options=chrome_options
            )
            
            # Configuración stealth mejorada
            stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )

            # Ejecutar scripts anti-detección adicionales
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": selected_user_agent
            })
            
            logger.info("Selenium WebDriver inicializado con configuración anti-detección mejorada")
            
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise

    def open_url(self, url, delay_range=(2, 5)):
        """Abrir URL con delay aleatorio para simular comportamiento humano"""
        logger.info(f"Opening URL: {url}")
        self.driver.get(url)
        
        # Delay aleatorio después de cargar la página
        delay = random.uniform(delay_range[0], delay_range[1])
        time.sleep(delay)
        
        # Simular scroll aleatorio
        self.random_scroll()

    def random_scroll(self):
        """Simular scroll aleatorio para parecer más humano"""
        try:
            # Scroll hacia abajo un poco
            scroll_height = random.randint(100, 300)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_height});")
            time.sleep(random.uniform(0.5, 1.5))
            
            # Scroll hacia arriba
            self.driver.execute_script(f"window.scrollBy(0, -{scroll_height//2});")
            time.sleep(random.uniform(0.5, 1.0))
        except Exception as e:
            logger.debug(f"Error en random_scroll: {e}")

    def find_element(self, by, value, timeout=10):
        """Find an element on the page."""
        logger.info(f"Finding element by {by} with value '{value}' (timeout={timeout}s).")
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            logger.info(f"Element found: {value}")
            return element
        except TimeoutException:
            logger.error(f"Element not found: {value}")
            return None

    def click_element(self, by, value, timeout=10):
        """Click an element with human-like behavior."""
        logger.info(f"Attempting to click element by {by} with value '{value}'.")
        element = self.find_element(by, value, timeout)
        if element:
            # Pequeño delay antes del click
            time.sleep(random.uniform(0.1, 0.3))
            element.click()
            logger.info(f"Clicked element: {value}")
            # Pequeño delay después del click
            time.sleep(random.uniform(0.1, 0.5))

    def send_keys(self, by, value, keys, timeout=10, typing_delay=True):
        """Send keys to an input element with human-like typing."""
        logger.info(f"Sending keys to element by {by} with value '{value}'.")
        element = self.find_element(by, value, timeout)
        if element:
            if typing_delay:
                # Simular escritura humana
                for char in keys:
                    element.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
            else:
                element.send_keys(keys)
            logger.info(f"Keys sent to element: {value}")

    def get_text(self, by, value, timeout=10):
        """Get text from an element."""
        logger.info(f"Getting text from element by {by} with value '{value}'.")
        element = self.find_element(by, value, timeout)
        if element:
            text = element.text
            logger.info(f"Text retrieved: {text}")
            return text
        logger.warning(f"Failed to retrieve text from element: {value}")
        return None

    def wait_and_get_text(self, by, value, timeout=15, max_retries=3):
        """Método mejorado para obtener texto con reintentos"""
        for attempt in range(max_retries):
            try:
                logger.info(f"Intento {attempt + 1} de obtener texto de {value}")
                
                # Esperar a que el elemento sea visible y tenga texto
                element = WebDriverWait(self.driver, timeout).until(
                    lambda driver: driver.find_element(by, value) and 
                                 driver.find_element(by, value).text.strip()
                )
                
                text = element.text.strip()
                if text:
                    logger.info(f"Texto obtenido exitosamente: {text}")
                    return text
                else:
                    logger.warning(f"Elemento encontrado pero sin texto en intento {attempt + 1}")
                    
            except Exception as e:
                logger.warning(f"Error en intento {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    delay = random.uniform(2, 4)
                    time.sleep(delay)
                    # Scroll aleatorio antes del siguiente intento
                    self.random_scroll()
        
        logger.error(f"No se pudo obtener texto después de {max_retries} intentos")
        return None

    def close_browser(self):
        """Close the browser."""
        logger.info("Closing the browser.")
        try:
            self.driver.quit()
        except Exception as e:
            logger.warning(f"Error al cerrar navegador: {e}")