import logging
import configparser
import pandas as pd
from pathlib import Path
from datetime import datetime
from utilidades.excepciones import BusinessException
import variables_globales as vg

logger = logging.getLogger("Bot 03 - Obtener Archivos BBVA")


def convertir_excel_a_txt(archivo_salida, moneda, ruta_excel):
    """
    Convierte un archivo Excel con datos de usuarios al formato TXT requerido

    Args:
        archivo_salida: Ruta del archivo TXT de salida (opcional)
        moneda: Moneda a usar en el archivo ("USD" para dólares, "PEN" para soles)
        ruta_excel: Ruta del archivo Excel a procesar
    """

    # Leer el archivo Excel
    try:
        df = pd.read_excel(ruta_excel)
        print(f"Archivo Excel leído exitosamente. Registros encontrados: {len(df)}")
    except Exception as e:
        print(f"Error al leer el archivo Excel: {e}")
        return

    # Validar columnas requeridas
    columnas_requeridas = ['TipoDocumento', 'NumeroDocumento', 'NombreCompleto', 'BIN']
    for col in columnas_requeridas:
        if col not in df.columns:
            print(f"Error: Columna '{col}' no encontrada en el archivo Excel")
            return

    # Generar nombre de archivo de salida si no se proporciona
    if archivo_salida is None:
        fecha_actual = datetime.now().strftime("%Y%m%d")
        moneda_nombre = "dolares" if moneda == "USD" else "soles"
        archivo_salida = f"RECAUDO_12159_{fecha_actual}_01_{moneda_nombre}.TXT"

    # Función para formatear nombre (máximo 30 caracteres)
    def formatear_nombre_largo(nombre, longitud=30):
        nombre = str(nombre).upper().strip()
        if len(nombre) > longitud:
            nombre = nombre[:longitud]
        return nombre.ljust(longitud)

    # Función para formatear nombre corto (máximo 28 caracteres)
    def formatear_nombre_corto(nombre, longitud=28):
        nombre = str(nombre).upper().strip()
        if len(nombre) > longitud:
            nombre = nombre[:longitud]
        return nombre.ljust(longitud)

    # Función para formatear documento (8 caracteres)
    def formatear_documento(doc):
        doc = str(doc).strip()
        return doc.ljust(8)

    # Crear el archivo TXT
    with open(archivo_salida, 'w', encoding='utf-8') as archivo:

        # LÍNEA HEADER (01)
        # Formato: 01 + info del archivo + padding hasta 360 caracteres
        bin_value = str(df.iloc[0]['BIN']) if 'BIN' in df.columns and not pd.isna(df.iloc[0]['BIN']) else "489000"
        fecha_proceso = datetime.now().strftime("%Y%m%d")  # Fecha actual YYYYMMDD

        header = "01"  # Tipo de registro
        header += "20537140489"  # RUC EMPRESA (código fijo)
        header += "000"  # NRO CLASE (siempre 000)
        header += moneda  # Moneda (USD o PEN)
        header += fecha_proceso  # Fecha actual
        header += "011"  # Versión (siempre 011)
        header += " " * 7  # Espacios
        header += "P"  # Tipo de proceso

        # Rellenar con espacios hasta 360 caracteres
        header = header.ljust(360)
        archivo.write(header + '\n')

        # LÍNEAS DE DETALLE (02)
        for index, row in df.iterrows():
            linea = "02"  # Tipo de registro

            # Nombre completo (30 caracteres)
            nombre_largo = formatear_nombre_largo(row['NombreCompleto'], 30)
            linea += nombre_largo

            # Número de documento (8 caracteres)
            documento = formatear_documento(row['NumeroDocumento'])
            linea += documento

            # Espacios de relleno (12 caracteres)
            linea += " " * 12

            # Nombre corto (28 caracteres) - versión truncada del nombre
            nombre_corto = formatear_nombre_corto(row['NombreCompleto'], 28)
            linea += nombre_corto

            # Fecha de inicio (8 caracteres) - formato YYYYMMDD
            fecha_inicio = "20391231"  # Fecha fija como en el ejemplo
            linea += fecha_inicio

            # Fecha de fin (8 caracteres) - formato YYYYMMDD  
            fecha_fin = "20391231"  # Fecha fija como en el ejemplo
            linea += fecha_fin

            # Rellenar con espacios hasta 360 caracteres
            linea = linea.ljust(360)
            archivo.write(linea + '\n')

        # LÍNEA DE TOTAL (03)
        total_registros = str(len(df)).zfill(9)  # 9 dígitos con ceros a la izquierda
        linea_total = "03"  # Tipo de registro
        linea_total += "000000"  # Ceros de relleno
        linea_total += total_registros  # Total de registros
        linea_total += "0" * 52  # Ceros de relleno adicional

        # Rellenar con espacios hasta 360 caracteres
        linea_total = linea_total.ljust(360)
        archivo.write(linea_total + '\n')

    print(f"Archivo TXT generado exitosamente: {archivo_salida}")
    print(f"Total de registros procesados: {len(df)}")
    print(f"Moneda utilizada: {moneda}")

# Función para generar TXT en dólares
def generar_txt_dolares(archivo_salida, ruta_excel):
    """Genera archivo TXT con moneda en dólares (USD)"""
    return convertir_excel_a_txt(archivo_salida, "USD", ruta_excel)

# Función para generar TXT en soles
def generar_txt_soles(archivo_salida, ruta_excel):
    """Genera archivo TXT con moneda en soles (PEN)"""
    return convertir_excel_a_txt(archivo_salida, "PEN", ruta_excel)


def bot_run(cfg, mensaje="Bot 03 - Obtener Archivos BBVA"):
    resultado = False
    try:
        logger.info("Iniciando ejecución del bot_run.")      
        input_path = Path(cfg["rutas"]["ruta_input"])
        logger.debug(f"Ruta de input: {vg.archivo_recaudo}")
        
        logger.info(f"Leyendo archivo de reporte: {vg.archivo_recaudo}")
        generar_txt_dolares(cfg["rutas"]["ruta_output"] + "/dolares.txt", vg.archivo_recaudo)
        generar_txt_soles(cfg["rutas"]["ruta_output"] + "/soles.txt", vg.archivo_recaudo)
        # Leer el archivo Excel y seleccionar/renombrar las columnas relevantes
        mensaje = f"Reporte procesado y validado correctamente."
        resultado = True
        logger.info("Archivo procesado y guardado correctamente.")
    except BusinessException as be:
        logger.error(f"Error de negocio en bot_run: {be}")
        mensaje = f"Error de negocio: {be}"
    except Exception as e:
        logger.error(f"Error inesperado en bot_run: {e}")
        mensaje = f"Error inesperado: {e}"
    finally:
        logger.info("Fin del bot: %s", mensaje)
        return resultado, mensaje