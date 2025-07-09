from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from selenium_stealth import stealth
from selenium.webdriver.common.action_chains import ActionChains
import logging
import os
import platform
from pathlib import Path
import variables_globales as vg 

logger = logging.getLogger("Bot 05 - Cargar BBVA Dólares")

#Función para imprimir la información de un elemento de html
def print_element_info(elemento):
    logger.debug("Ejecutando print_element_info")
    children = elemento.find_elements(By.CSS_SELECTOR, "*")
    # Imprimir tag y clase
    for child in children:
        print(child.tag_name, "-", child.get_attribute("class"))

def create_stealth_webdriver(cfg):
    logger.info("Creando instancia de Chrome WebDriver con stealth.")
    """
    Crea un driver de Chrome configurado para descargar archivos en la ruta indicada en cfg['rutas']['ruta_input']
    """
    download_path = str(Path(cfg['rutas']['ruta_input']).absolute())
    profile_dir = str(Path(cfg['rutas']['ruta_perfil_bbva_soles']).absolute())
    options = webdriver.ChromeOptions()
    # options.add_argument(f"user-data-dir={profile_dir}")
    
    # Argumentos anti-detección mejorados
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-first-run")
    options.add_argument("--no-service-autorun")
    options.add_argument("--password-store=basic")
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    
    # User agent más actualizado
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')

    prefs = {
        "download.default_directory": download_path,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
        "profile.managed_default_content_settings.images": 1,
        "profile.default_content_setting_values.cookies": 1,
        "profile.block_third_party_cookies": False,
        "profile.default_content_setting_values.plugins": 1,
        "profile.content_settings.plugin_whitelist.adobe-flash-player": 1,
        "profile.content_settings.exceptions.plugins.*,*.per_resource.adobe-flash-player": 1
    }
    options.add_experimental_option("prefs", prefs)

    # Set longer timeout for ChromeDriver installation
    os.environ['PYDEVD_WARN_EVALUATION_TIMEOUT'] = '30'  # 30 seconds timeout
    os.environ['PYDEVD_UNBLOCK_THREADS_TIMEOUT'] = '30'  # Unblock threads after 30 seconds
    logger.info("Instalando ChromeDriver y lanzando navegador.")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Ejecutar scripts anti-detección adicionales
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['es-ES', 'es']})")
    driver.execute_script("window.chrome = {runtime: {}}")

    stealth(driver,
        languages=["es-ES", "es"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    logger.info("WebDriver creado y configurado con stealth.")
    return driver

def cargar_bbva_soles_navegacion(cfg):
    """
    Función principal que ejecuta todo el proceso de navegación Cargar BBVA DÓLARES
    """
    driver = None
    try:
        logger.info("Iniciando proceso completo de navegación Cargar BBVA DÓLARES")
        driver = create_stealth_webdriver(cfg)

        def retry_login(max_attempts=int(cfg['reintentos']['reintentos_max'])):
            for attempt in range(max_attempts):
                try:
                    logger.info(f"Intento de login {attempt + 1}/{max_attempts}")
                    login(driver, cfg)
                    logger.info("Login exitoso")
                    return True
                except Exception as e:
                    logger.warning(f"Error en intento {attempt + 1}: {e}")
                    if attempt < max_attempts - 1:
                        logger.info("Actualizando página y reintentando login...")
                        driver.refresh()
                        time.sleep(5)
                    else:
                        logger.error("Se agotaron todos los intentos de login")
                        raise e
            return False

        retry_login()
        
        # Reintentar desde selección de cobros si hay problemas
        max_flow_attempts = int(cfg['reintentos']['reintentos_max'])
        for flow_attempt in range(max_flow_attempts):
            try:
                logger.info(f"Intento de flujo desde cobros {flow_attempt + 1}/{max_flow_attempts}")
                select_charges(driver)
                upload_file(driver)
            except Exception as e:
                logger.warning(f"Error en flujo intento {flow_attempt + 1}: {e}")
                if flow_attempt < max_flow_attempts - 1:
                    logger.info("Reiniciando desde selección de cobros...")
                    # Solo volver al contexto principal, no recargar página completa
                    driver.switch_to.default_content()
                    time.sleep(3)
                else:
                    logger.error("Se agotaron todos los intentos de flujo")
                    raise e
        
        return False
    except Exception as e:
        logger.error(f"Ocurrió un error en cargar_bbva_soles_navegacion: {e}")
        return False
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("Driver cerrado correctamente")
            except Exception:
                logger.warning("Error al cerrar el driver")

def login(driver, cfg):
    """
    Realiza el proceso de login en BBVA Netcash. Si falla, lanza una excepción.
    """
    try:
        logger.info("Iniciando login BBVA Netcash")
        wait = WebDriverWait(driver, 15)

        # Limpiar cookies y storage
        driver.delete_all_cookies()
        driver.get(cfg['url']['url_bbva'])
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")
        time.sleep(5)  # Espera para carga inicial

        # Ingresar código de empresa - esperar que esté presente y sea clickeable
        company_code_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='cod_emp']"))
        )
        company_code_input.clear()
        company_code_input.send_keys(cfg['env_vars']['bbva']['code'])
        time.sleep(1)

        # Ingresar código de usuario - esperar que esté presente y sea clickeable
        user_code_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='cod_usu']"))
        )
        user_code_input.clear()
        user_code_input.send_keys(cfg['env_vars']['bbva']['user'])
        time.sleep(1)

        # Ingresar contraseña - esperar que esté presente y sea clickeable
        password_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='eai_password']"))
        )
        password_input.clear()
        password_input.send_keys(cfg['env_vars']['bbva']['password'])
        time.sleep(3)

        # Click en Ingresar - esperar que el botón esté clickeable
        login_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Ingresar']"))
        )
        driver.execute_script("arguments[0].click();", login_button)
        time.sleep(10)

        # Refrescar después del login
        driver.refresh()
        time.sleep(3)

        logger.info("Login exitoso en BBVA Netcash")

    except Exception as e:
        logger.error(f"Error durante el login BBVA Netcash: {e}")
        raise e

def select_charges(driver):
    logger.info("Seleccionando menú de cobros en la interfaz BBVA.")
    wait = WebDriverWait(driver, 15)
    time.sleep(5)
    app_template_host = driver.find_element(By.CSS_SELECTOR, "bbva-btge-app-template")
    app_template_shadow_root = driver.execute_script("return arguments[0].shadowRoot", app_template_host)

    sidebar_menu_host = driver.find_element(By.CSS_SELECTOR, "bbva-btge-sidebar-menu")
    sidebar_menu_shadow_root = driver.execute_script("return arguments[0].shadowRoot", sidebar_menu_host)

    charges_menu_item = sidebar_menu_shadow_root.find_element(
        By.CSS_SELECTOR,
        "bbva-web-navigation-menu-item[icon='bbva:paysheetdollar']"
    )
    charges_menu_item.click()
    time.sleep(3)
    logger.info("Menú de cobros seleccionado.")

def upload_file(driver):
    logger.info("Entrando al iframe principal.")
    # Step 1: locate the main shadow host
    main_shadow_host = driver.find_element(By.CSS_SELECTOR, "bbva-btge-menurization-landing-solution-page")
    main_shadow_root = driver.execute_script("return arguments[0].shadowRoot", main_shadow_host)

    # Step 2: locate iframe inside first shadow DOM
    iframe_host = main_shadow_root.find_element(By.CSS_SELECTOR, "bbva-core-iframe")
    iframe_shadow_root = driver.execute_script("return arguments[0].shadowRoot", iframe_host)
    core_iframe_element = iframe_shadow_root.find_element(By.CSS_SELECTOR, "iframe")
    driver.switch_to.frame(core_iframe_element)

    time.sleep(3)
    logger.info("Se ha entrado al iframe correctamente.")

    layout_shadow_host = driver.find_element(By.CSS_SELECTOR, "bbva-btge-menurization-landing-solution-home-page")
    layout_shadow_root = driver.execute_script("return arguments[0].shadowRoot", layout_shadow_host)
    link_elements = layout_shadow_root.find_elements(By.CSS_SELECTOR, "bbva-web-link")
    for link_element in link_elements:
        link_text = link_element.text.strip()

        # Step 5: look for 'Recaudos pagados' link and click it
        if link_text == "Cargar archivo":
            print("Found 'Cargar archivo', clicking the link.")
            logger.info("Encontrado enlace 'Cargar archivo', haciendo clic.")
            link_element.click()
            break
    time.sleep(5)
    
    driver.switch_to.default_content()
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "legacy-page"))
    )
    legacy_page_host = driver.find_element(By.CSS_SELECTOR, "legacy-page")
    legacy_page_shadow_root = driver.execute_script("return arguments[0].shadowRoot", legacy_page_host)
    # Step 2: enter shadowRoot of bbva-core-iframe
    iframe_host = legacy_page_shadow_root.find_element(By.CSS_SELECTOR, "bbva-core-iframe")
    iframe_shadow_root = driver.execute_script("return arguments[0].shadowRoot", iframe_host)

    # Step 3: switch to internal iframe inside bbva-core-iframe → iframe#bbvaIframe
    core_iframe_element = iframe_shadow_root.find_element(By.CSS_SELECTOR, "iframe")
    driver.switch_to.frame(core_iframe_element)

    # Optional: log when inside iframe
    print("Inside iframe#bbvaIframe")
    logger.debug("Dentro del iframe #bbvaIframe.")


    kyop_iframe_element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#kyop-central-load-area")))
    driver.switch_to.frame(kyop_iframe_element)

    print("Inside iframe#kyop-central-load-area")
    logger.debug("Dentro del iframe #kyop-central-load-area.")
    time.sleep(2)

    # Esperar hasta que el radio button de DÓLARES esté presente y hacerle click
    logger.info("Esperando el radio button de DÓLARES y haciendo click...")
    radio_dolares = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@type='radio' and @class='botonradio' and contains(@onclick, 'DOLARES')]")
        )
    )
    driver.execute_script("arguments[0].click();", radio_dolares)
    logger.info("Click en el radio button de DÓLARES realizado correctamente.")
    # Esperar hasta que el botón 'Continuar' esté presente y hacerle clic
    logger.info("Esperando el botón 'Continuar' y haciendo click...")
    boton_continuar = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//input[@type='button' and @value='Continuar']")
        )
    )
    driver.execute_script("arguments[0].click();", boton_continuar)
    logger.info("Click en el botón 'Continuar' realizado correctamente.")
    # Esperar hasta que el radio button de "incorpor" esté presente y hacerle click
    logger.info("Esperando el radio button de 'incorpor' y haciendo click...")
    radio_incorpor = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@type='radio' and contains(@onclick, 'incorpor')]")
        )
    )
    driver.execute_script("arguments[0].click();", radio_incorpor)
    logger.info("Click en el radio button de 'incorpor' realizado correctamente.")

    # Usar JavaScript para establecer el valor del input file (no siempre funciona por restricciones de seguridad del navegador)
    # Se asume que ruta_archivo es una variable con la ruta absoluta al archivo a subir
    input_file = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@type='file' and @name='ficheroIncorpora']")
        )
    )
    # Intentar con send_keys tradicional primero (es lo más robusto)
    time.sleep(4)
    # Buscar el input file y hacerlo visible
    file_input = driver.find_element(By.XPATH, "//input[@type='file']")
        
    # Hacer visible el input si está oculto
    driver.execute_script("arguments[0].style.display = 'block';", file_input)
        
    # Enviar la ruta del archivo
    file_input.send_keys(vg.archivo_recaudo)
        
    logger.info(f"Archivo {vg.archivo_recaudo} cargado exitosamente")
    time.sleep(2)

    # Esperar hasta que el botón 'Continuar' con id 'btnEnviar' esté presente y hacerle clic
    logger.info("Esperando el botón 'Continuar' y haciendo click...")
    boton_enviar = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//input[@type='button' and @id='btnEnviar' and @value='Continuar']")
        )
    )
    driver.execute_script("arguments[0].click();", boton_enviar)
    logger.info("Click en el botón 'Continuar' realizado correctamente.")
    time.sleep(2)

    WebDriverWait(driver, 10).until(EC.alert_is_present())
    alert = driver.switch_to.alert
    logger.info(f"Confirmando: {alert.text}")
    alert.accept()  # Hace clic en "Aceptar"
    logger.info("Carga de archivo confirmada")
    time.sleep(5) 

    # Verificar si aparece el mensaje de error por estructura incorrecta del archivo txt
    try:
        # Esperar un máximo de 5 segundos por el mensaje de error específico
        mensaje_error = True
        mensaje_error = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@class='msj_ico msj_err']")
            )
        )
    except Exception:
        mensaje_error = False
        pass

    if mensaje_error:
        logger.error("La estructura del archivo txt no es correcta. Abortando proceso de carga.")
        return False
    else:
        logger.info("La estructura del archivo txt es correcta. Se realizó proceso de carga.")
        return True
    #

def bot_run(cfg, mensaje):
    logger.info("Iniciando ejecución de bot_run para Cargar BBVA Dólares.")
    try:
        resultado = False   
        logger.info("Iniciando ejecución principal del bot Cargar BBVA Dólares")
        
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                logger.info(f"Intento de navegación {attempt + 1}/{max_attempts}")
                resultado = cargar_bbva_soles_navegacion(cfg)
                if resultado:
                    logger.info("Navegación exitosa hasta iframe")
                    break
                else:
                    logger.warning(f"Navegación fallida en intento {attempt + 1}")
                    if attempt < max_attempts - 1:
                        time.sleep(5)  # Esperar 5 segundos antes del siguiente intento
            except Exception as e:
                logger.error(f"Error en intento {attempt + 1}: {e}")
                if attempt < max_attempts - 1:
                    logger.info("Reintentando navegación...")
                    time.sleep(5)
                else:
                    logger.error("Se agotaron todos los intentos de navegación")
                    raise e
        
        if resultado:
            mensaje = "Navegación exitosa hasta iframe"
        else:
            mensaje = "Navegación no exitosa"

    except Exception as e:
        logger.error(f"Error en bot Cargar BBVA Dólares: {e}")
        if platform.system() == 'Windows':
            os.system("taskkill /im chrome.exe /f")
        else:
            os.system("pkill -f chrome")
        raise Exception(f"Error en bot Cargar BBVA Dólares: {e}") from e

    finally:
        logger.info("Navegador cerrado")
        return resultado, mensaje