import logging
import configparser
import polars as pl
from pathlib import Path
from utilidades.excepciones import BusinessException

logger = logging.getLogger("Bot 02 - Procesar Reporte")

def procesar_df(df: pl.DataFrame) -> pl.DataFrame:
    """
    Procesa el DataFrame para limpiar y validar los datos.
    """
    logger.info("Iniciando procesamiento del DataFrame.")
    
    # Renombrar columnas para facilitar el acceso
    column_names = df.columns
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
            df = df.rename(rename_map)
            logger.info(f"Columnas renombradas. Nuevos nombres: {df.columns}")
        else:
            logger.info("No se necesitaron renombres de columnas.")

    else:
        raise BusinessException("El archivo Excel no tiene el número de columnas esperado.")

    # Limpieza de datos
    df = df.with_columns([
        pl.col("Nombres").str.strip_chars().str.to_uppercase().str.replace_all(r"[^A-Z\sÑÁÉÍÓÚÜ]", ""),
        pl.col("Tipo Documento").str.strip_chars().str.to_uppercase(),
        pl.col("Numero Documento").cast(pl.Utf8).str.strip_chars()
    ])
    logger.info("Columnas de texto limpiadas (espacios, caracteres extraños).")

    # Validación de número de documento
    validation_rules = {'DI': 8, 'RUC': 11}
    
    # Usando replace (antes map_dict) para la validación
    expected_length = pl.col("Tipo Documento").replace(validation_rules, default=0)
    
    invalid_docs = df.filter(pl.col("Numero Documento").str.len_chars() != expected_length)

    if not invalid_docs.is_empty():
        # Log de hasta 5 filas inválidas para no sobrecargar el log
        logger.warning(f"Se encontraron {len(invalid_docs)} filas con número de documento inválido.")
        log_sample = invalid_docs.head(5)
        logger.warning("Ejemplos de filas inválidas:")
        logger.warning(log_sample.to_dict(as_series=False))
        # Opcional: lanzar una excepción si se requiere detener el proceso
        # raise BusinessException(f"Se encontraron {len(invalid_docs)} filas con número de documento inválido.")

    logger.info("Procesamiento del DataFrame completado.")
    return df

def bot_run(cfg, mensaje="Bot 02 - Procesar Reporte"):
    resultado = False
    try:
        # Leer configuración
        config = configparser.ConfigParser()
        config.read(cfg)
        input_path = Path(cfg["rutas"]["ruta_input"])
        path_reporte = input_path / "recaudo.xls"
        df = pl.read_excel(path_reporte)
        logger.info(f"Reporte leido correctamente")

        df_procesado = procesar_df(df)

        logger.info(f"DataFrame procesado con éxito. Shape: {df_procesado.shape}")
        
        # Aquí puedes guardar el df_procesado o pasarlo a la siguiente etapa
        # Por ejemplo, guardarlo en un nuevo archivo:
        # output_path = Path(config['rutas']['ruta_output'])
        # df_procesado.write_csv(output_path / "reporte_procesado.csv")

        mensaje = f"Reporte procesado y validado correctamente."
        resultado = True
    except BusinessException as be:
        logger.error(f"Error de negocio en bot_run: {be}")
        mensaje = f"Error de negocio: {be}"
    except Exception as e:
        logger.error(f"Error inesperado en bot_run: {e}")
        mensaje = f"Error inesperado: {e}"
    finally:
        logger.info("Fin del bot: %s", mensaje)
        return resultado, mensaje