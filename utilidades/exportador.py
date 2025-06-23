import os
import json
import csv
import xlsxwriter
from fpdf import FPDF
import logging

# Configurar el logger
logger = logging.getLogger("Utils - Exportador")

class Exportador:
    def __init__(self, ruta_output):
        """
        Inicializa el exportador con la ruta de salida configurada.

        :param ruta_output: Directorio donde se guardarán los archivos exportados.
        """
        self.ruta_output = ruta_output
        os.makedirs(self.ruta_output, exist_ok=True)

    def exportar_json(self, data, nombre_archivo):
        """
        Exporta datos a un archivo JSON.

        :param data: Los datos a exportar (deben ser serializables en JSON).
        :param nombre_archivo: El nombre del archivo JSON (sin extensión).
        """
        ruta_completa = os.path.join(self.ruta_output, f"{nombre_archivo}.json")
        try:
            with open(ruta_completa, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            logger.info(f"Archivo JSON guardado en {ruta_completa}")
        except Exception as e:
            logger.error(f"Error al exportar JSON: {e}")
            raise

    def exportar_txt(self, data, nombre_archivo):
        """
        Exporta datos a un archivo de texto.

        :param data: Los datos a exportar (deben ser una lista o diccionario).
        :param nombre_archivo: El nombre del archivo de texto (sin extensión).
        """
        ruta_completa = os.path.join(self.ruta_output, f"{nombre_archivo}.txt")
        try:
            with open(ruta_completa, 'w', encoding='utf-8') as file:
                if isinstance(data, dict):
                    for key, value in data.items():
                        file.write(f"{key}: {value}\n")
                elif isinstance(data, list):
                    for item in data:
                        file.write(f"{item}\n")
            logger.info(f"Archivo TXT guardado en {ruta_completa}")
        except Exception as e:
            logger.error(f"Error al exportar TXT: {e}")
            raise

    def exportar_csv(self, data, nombre_archivo):
        """
        Exporta datos a un archivo CSV.

        :param data: Los datos a exportar (deben ser una lista de diccionarios).
        :param nombre_archivo: El nombre del archivo CSV (sin extensión).
        """
        ruta_completa = os.path.join(self.ruta_output, f"{nombre_archivo}.csv")
        try:
            with open(ruta_completa, 'w', newline='', encoding='utf-8') as file:
                if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                    writer = csv.DictWriter(file, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                else:
                    raise ValueError("Los datos para CSV deben ser una lista de diccionarios.")
            logger.info(f"Archivo CSV guardado en {ruta_completa}")
        except Exception as e:
            logger.error(f"Error al exportar CSV: {e}")
            raise

    def exportar_xlsx(self, data, nombre_archivo):
        """
        Exporta datos a un archivo XLSX.

        :param data: Los datos a exportar (deben ser una lista de diccionarios).
        :param nombre_archivo: El nombre del archivo XLSX (sin extensión).
        """
        ruta_completa = os.path.join(self.ruta_output, f"{nombre_archivo}.xlsx")
        try:
            workbook = xlsxwriter.Workbook(ruta_completa)
            worksheet = workbook.add_worksheet()
            if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                headers = data[0].keys()
                for col, header in enumerate(headers):
                    worksheet.write(0, col, header)
                for row, item in enumerate(data, start=1):
                    for col, (key, value) in enumerate(item.items()):
                        worksheet.write(row, col, value)
            else:
                raise ValueError("Los datos para XLSX deben ser una lista de diccionarios.")
            workbook.close()
            logger.info(f"Archivo XLSX guardado en {ruta_completa}")
        except Exception as e:
            logger.error(f"Error al exportar XLSX: {e}")
            raise

    def exportar_pdf(self, data, nombre_archivo):
        """
        Exporta datos a un archivo PDF.

        :param data: Los datos a exportar (deben ser una lista o diccionario).
        :param nombre_archivo: El nombre del archivo PDF (sin extensión).
        """
        ruta_completa = os.path.join(self.ruta_output, f"{nombre_archivo}.pdf")
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            if isinstance(data, dict):
                for key, value in data.items():
                    pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
            elif isinstance(data, list):
                for item in data:
                    pdf.cell(200, 10, txt=str(item), ln=True)
            pdf.output(ruta_completa)
            logger.info(f"Archivo PDF guardado en {ruta_completa}")
        except Exception as e:
            logger.error(f"Error al exportar PDF: {e}")
            raise