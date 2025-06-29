import logging
import configparser
import polars as pl
from pathlib import Path
from datetime import datetime
from utilidades.excepciones import BusinessException

logger = logging.getLogger("Bot 02 - Procesar Reporte")

def procesar_df(df: pl.DataFrame) -> pl.DataFrame:
    """
    Procesa el DataFrame para limpiar y validar los datos.
    """
    logger.info("Iniciando procesamiento del DataFrame.")
    
    # Renombrar columnas para facilitar el acceso
    column_names = df.columns
    logger.debug(f"Columnas originales del DataFrame: {column_names}")
    if len(column_names) > 4:
        # Nombres de columna deseados y sus posiciones esperadas si no existen
        desired_columns = {
            "Tipo Documento": 2,
            "Numero Documento": 3,
            "Nombres": 4
        }
        
        rename_map = {}
        current_columns = list(df.columns)

        for name, index in desired_columns.items():
            # Si el nombre deseado no está en las columnas y el índice es válido
            if name not in current_columns and index < len(current_columns):
                # Y el nombre actual en esa posición no es ya un nombre deseado
                if current_columns[index] not in desired_columns:
                    rename_map[current_columns[index]] = name

        if rename_map:
            logger.info(f"Renombrando columnas: {rename_map}")
            df = df.rename(rename_map)
            logger.info(f"Columnas renombradas. Nuevos nombres: {df.columns}")
        else:
            logger.info("No se necesitaron renombres de columnas.")

        # Paso 2: Juntar columnas de nombre y apellidos en una sola columna "Nombres"
        # NOTA: .str.strip() no existe en polars, usar solo .str.strip_chars() para limpiar espacios
        logger.debug("Verificando si existen columnas de apellidos y nombres para unirlas.")
        if all(col in df.columns for col in ["Apellido Paterno", "Apellido Materno", "Nombres"]):
            logger.info("Unificando columnas 'Apellido Paterno', 'Apellido Materno' y 'Nombres' en 'Nombres'.")
            df = df.with_columns([
                (
                    pl.col("Apellido Paterno").cast(pl.Utf8).str.strip_chars()
                    + pl.lit(" ")
                    + pl.col("Apellido Materno").cast(pl.Utf8).str.strip_chars()
                    + pl.lit(" ")
                    + pl.col("Nombres").cast(pl.Utf8).str.strip_chars()
                ).str.replace_all(r"\s+", " ").str.strip_chars().alias("Nombres_Completos")
            ])
            # Eliminar columnas originales y dejar solo "Nombres"
            df = df.drop(["Apellido Paterno", "Apellido Materno", "Nombres"])
            df = df.rename({"Nombres_Completos": "Nombres"})
            logger.info("Columnas de nombre y apellidos unidas en 'Nombres'.")
        else:
            logger.warning("No se encontraron todas las columnas de nombre y apellidos para unir.")

        # Paso 3: Limpiar caracteres extraños en columnas relevantes
        logger.info("Limpiando caracteres extraños y espacios en columnas relevantes.")
        df = df.with_columns([
            pl.col("Nombres").str.strip_chars().str.to_uppercase().str.replace_all(r"[^A-Z\sÑÁÉÍÓÚÜ]", ""),
            pl.col("Tipo Documento").str.strip_chars().str.to_uppercase(),
            pl.col("Numero Documento").str.strip_chars()
        ])
        logger.info("Columnas de texto limpiadas (espacios, caracteres extraños).")

        # Paso 4: Validar longitud de Numero Documento según Tipo Documento
        logger.info("Validando longitud de 'Numero Documento' según 'Tipo Documento'.")
        validation_rules = {'DI': 8, 'RUC': 11, 'PT': 12, 'CE': 9}
        expected_length = pl.col("Tipo Documento").replace(validation_rules, default=0)
        invalid_docs = df.filter(pl.col("Numero Documento").str.len_chars() != expected_length)
        if not invalid_docs.is_empty():
            logger.warning(f"Se encontraron {len(invalid_docs)} filas con número de documento inválido.")
            log_sample = invalid_docs.head(5)
            logger.warning("Ejemplos de filas inválidas:")
            logger.warning(log_sample.to_dict(as_series=False))
        else:
            logger.info("Todos los números de documento cumplen con la longitud esperada.")

        # Paso 5: Si Tipo Documento in ('DI','PT','CE'), evaluar Bin in ('489486','422826','519115','483179')
        # Se asume que existe una columna 'Bin' (si no, este paso se omite)
        bin_values = {'489486', '422826', '519115', '483179'}
        if "Bin" in df.columns:
            logger.info("Validando y limpiando columna 'Bin' para tipos de documento DI, PT, CE.")
            mask_tipo = pl.col("Tipo Documento").is_in(["DI", "PT", "CE"])
            mask_bin = pl.col("Bin").is_in(list(bin_values))
            # Todas las columnas ya son string, y polars no tiene .str.strip(), usar .str.strip_chars()
            df = df.with_columns([
                pl.when(mask_tipo & mask_bin)
                .then(pl.col("Bin").str.strip_chars())
                .otherwise(pl.col("Bin"))
                .alias("Bin")
            ])
            logger.info("Validación y limpieza de columna 'Bin' aplicada para tipos de documento DI, PT, CE.")
        else:
            logger.info("Columna 'Bin' no encontrada, se omite validación de Bin.")

    else:
        logger.error("El archivo Excel no tiene el número de columnas esperado.")
        raise BusinessException("El archivo Excel no tiene el número de columnas esperado.")

    # Limpieza de datos
    logger.info("Realizando limpieza final de columnas de texto.")
    df = df.with_columns([
        pl.col("Nombres").str.strip_chars().str.to_uppercase().str.replace_all(r"[^A-Z\sÑÁÉÍÓÚÜ]", ""),
        pl.col("Tipo Documento").str.strip_chars().str.to_uppercase(),
        pl.col("Numero Documento").cast(pl.Utf8).str.strip_chars()
    ])
    logger.info("Columnas de texto limpiadas (espacios, caracteres extraños).")

    # Validación de número de documento
    logger.info("Validando nuevamente la longitud de 'Numero Documento' para reglas finales.")
    validation_rules = {'DI': 8, 'RUC': 11}
    
    # Usando replace (antes map_dict) para la validación
    expected_length = pl.col("Tipo Documento").replace(validation_rules, default=0)
    
    invalid_docs = df.filter(pl.col("Numero Documento").str.len_chars() != expected_length)

    if not invalid_docs.is_empty():
        # Log de hasta 5 filas inválidas para no sobrecargar el log
        logger.warning(f"Se encontraron {len(invalid_docs)} filas con número de documento inválido (validación final).")
        log_sample = invalid_docs.head(5)
        logger.warning("Ejemplos de filas inválidas:")
        logger.warning(log_sample.to_dict(as_series=False))
        # Opcional: lanzar una excepción si se requiere detener el proceso
        # raise BusinessException(f"Se encontraron {len(invalid_docs)} filas con número de documento inválido.")
    else:
        logger.info("Todos los números de documento cumplen con la longitud esperada (validación final).")

    logger.info("Procesamiento del DataFrame completado.")
    # Eliminar la columna 'Fecha Activacion' si existe
    if "Fecha Activacion" in df.columns:
        logger.info("Eliminando columna 'Fecha Activacion' del DataFrame.")
        df = df.drop("Fecha Activacion")
        logger.info("Columna 'Fecha Activacion' eliminada del DataFrame.")
    return df

def bot_run(cfg, mensaje="Bot 02 - Procesar Reporte"):
    resultado = False
    try:
        logger.info("Iniciando ejecución del bot_run.")
        # Leer configuración
        config = configparser.ConfigParser()
        logger.debug("Leyendo archivo de configuración.")
        config.read(cfg)
        input_path = Path(cfg["rutas"]["ruta_input"])
        logger.debug(f"Ruta de input: {input_path}")
        path_reporte = input_path / "recaudo.xls"
        logger.info(f"Leyendo archivo de reporte: {path_reporte}")
        # Leer el archivo Excel y seleccionar/renombrar las columnas relevantes
        df = pl.read_excel(path_reporte)

        logger.info("Archivo Excel leído correctamente.")
        # Castear todas las columnas a string (Utf8)
        for col in df.columns:
            df = df.with_columns(pl.col(col).cast(pl.Utf8).alias(col))
        logger.info(f"Reporte leído correctamente (todas las columnas casteadas a string)")

        logger.info("Procesando DataFrame con la función procesar_df.")
        df_procesado = procesar_df(df)

        logger.info(f"DataFrame procesado con éxito. Shape: {df_procesado.shape}")
        output_path = Path(config['rutas']['ruta_output'])
        logger.debug(f"Ruta de output: {output_path}")
        fecha_str = datetime.now().strftime("%Y%m%d%H%M%S")
        nombre_archivo = f"Reporte_Recaudacion_{fecha_str}.xlsx"
        logger.info(f"Guardando DataFrame procesado en: {output_path / nombre_archivo}")
        df_procesado.write_excel(output_path / nombre_archivo, include_index=False)
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