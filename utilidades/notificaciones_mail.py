import smtplib
import ssl
from email.message import EmailMessage
import logging

# Configuracionn del logger
logger = logging.getLogger("Utils - EmailSender")

class EmailSender:
    def __init__(self, servidor_smtp, puerto, usuario, contrasena):
        """
        Inicializa el remitente de correos electronicos.

        :param servidor_smtp: Dirección del servidor SMTP.
        :param puerto: Puerto del servidor SMTP.
        :param usuario: Nombre de usuario para autenticarse en el servidor.
        :param contrasena: Contraseña para autenticarse en el servidor.
        """
        self.servidor_smtp = servidor_smtp
        self.puerto = puerto
        self.usuario = usuario
        self.contrasena = contrasena

    def enviar_correo(self, destinatarios, asunto, cuerpo, adjuntos=None):
        try:
            # Creacion del mensaje de correo electrónico
            mensaje = EmailMessage()
            mensaje['From'] = self.usuario
            mensaje['To'] = ', '.join(destinatarios)
            mensaje['Subject'] = asunto
            mensaje.set_content(cuerpo)

            # Adjuntar archivos al correo
            if adjuntos:
                for adjunto in adjuntos:
                    try:
                        with open(adjunto, 'rb') as archivo:
                            nombre_archivo = adjunto.split('/')[-1]
                            mensaje.add_attachment(
                                archivo.read(),
                                maintype='application',
                                subtype='octet-stream',
                                filename=nombre_archivo
                            )
                            logger.info(f"Archivo adjunto agregado: {nombre_archivo}")
                    except Exception as e:
                        logger.error(f"No se pudo adjuntar el archivo {adjunto}: {e}")

            # Configuracion de la conexion segura al servidor SMTP
            context = ssl.create_default_context()

            with smtplib.SMTP_SSL(self.servidor_smtp, self.puerto, context=context) as server:
                server.login(self.usuario, self.contrasena)
                server.send_message(mensaje)
                logger.info(f"Correo enviado exitosamente a: {', '.join(destinatarios)}")

        except Exception as e:
            logger.error(f"Error al enviar el correo: {e}")