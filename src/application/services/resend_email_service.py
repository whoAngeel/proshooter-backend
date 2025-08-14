import resend
from fastapi import Depends
import logging
from sqlalchemy.orm import Session
from src.infraestructure.database.session import get_db
from src.infraestructure.config.settings import settings

logger = logging.getLogger(__name__)


class ResendEmailService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.sender_email = settings.RESEND_SENDER_EMAIL
        resend.api_key = settings.RESEND_API_KEY

    def send_password_reset_email(
        self, recipient_email: str, reset_token: str, frontend_url: str
    ) -> bool:
        reset_link = f"{frontend_url}/reset-password?token={reset_token}"

        # Template HTML del email
        html_content = f"""


        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Recuperación de Contraseña</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 600;">
                        🎯 Pro Shooter API
                    </h1>
                    <p style="color: #e8e8e8; margin: 10px 0 0 0; font-size: 16px;">
                        Sistema de Entrenamiento de Tiro
                    </p>
                </div>

                <!-- Body -->
                <div style="padding: 40px 30px;">
                    <h2 style="color: #333333; margin: 0 0 20px 0; font-size: 24px;">
                        🔐 Recuperación de Contraseña
                    </h2>

                    <p style="color: #555555; line-height: 1.6; margin: 0 0 20px 0; font-size: 16px;">
                        Hola,
                    </p>

                    <p style="color: #555555; line-height: 1.6; margin: 0 0 30px 0; font-size: 16px;">
                        Recibimos una solicitud para restablecer la contraseña de tu cuenta en
                        <strong>Pro Shooter API</strong>. Si fuiste tú, haz clic en el botón de abajo para continuar.
                    </p>

                    <!-- CTA Button -->
                    <div style="text-align: center; margin: 40px 0;">
                        <a href="{reset_link}"
                           style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                  color: #ffffff; text-decoration: none; padding: 16px 32px;
                                  border-radius: 8px; font-weight: 600; font-size: 16px;
                                  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
                            ✨ Restablecer Contraseña
                        </a>
                    </div>

                    <!-- Alert Box -->
                    <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 20px; margin: 30px 0;">
                        <h3 style="color: #856404; margin: 0 0 15px 0; font-size: 18px;">
                            ⚠️ Información Importante
                        </h3>
                        <ul style="color: #856404; margin: 0; padding-left: 20px; line-height: 1.6;">
                            <li>Este enlace <strong>expira en 30 minutos</strong></li>
                            <li>Solo puede usarse <strong>una vez</strong></li>
                            <li>Si no solicitaste este cambio, <strong>ignora este email</strong></li>
                        </ul>
                    </div>

                    <!-- Alternative Link -->
                    <div style="background-color: #f8f9fa; border-radius: 8px; padding: 20px; margin: 30px 0;">
                        <p style="color: #6c757d; margin: 0 0 10px 0; font-size: 14px;">
                            <strong>¿El botón no funciona?</strong> Copia y pega este enlace en tu navegador:
                        </p>
                        <p style="color: #495057; word-break: break-all; font-size: 12px;
                                  background-color: #ffffff; padding: 10px; border-radius: 4px;
                                  border: 1px solid #dee2e6; margin: 0;">
                            {reset_link}
                        </p>
                    </div>

                    <p style="color: #6c757d; line-height: 1.6; margin: 30px 0 0 0; font-size: 14px;">
                        Si tienes algún problema, no dudes en contactar con nuestro equipo de soporte.
                    </p>
                </div>

                <!-- Footer -->
                <div style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #dee2e6;">
                    <p style="color: #6c757d; margin: 0; font-size: 12px; line-height: 1.4;">
                        Este email fue enviado automáticamente por <strong>Pro Shooter API</strong>.<br>
                        No responder a este mensaje.
                    </p>
                    <p style="color: #6c757d; margin: 10px 0 0 0; font-size: 12px;">
                        © 2025 Pro Shooter API. Todos los derechos reservados.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        try:
            # enviar email usando resend
            email_data = {
                "from": self.sender_email,
                "to": [recipient_email],
                "subject": "🔐 Recuperación de Contraseña - Pro Shooter API",
                "html": html_content,
            }

            response = resend.Emails.send(email_data)
            logger.info(f"Email enviado exitosamente a {recipient_email}: {response}")
            return True
        except resend.exceptions.ResendError as e:
            logger.error(f"❌ Error al enviar email a {recipient_email}: {e}")
            return False
        except Exception as e:
            logger.error(
                f"❌ Error inesperado al enviar email a {recipient_email}: {e}"
            )
            return False

    def send_password_changed_notification(self, recipient_email: str) -> bool:
        """Enviar notificación de cambio de contraseña exitoso"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Contraseña Actualizada</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 40px 30px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 600;">
                        🎯 Pro Shooter API
                    </h1>
                    <p style="color: #e8f5e8; margin: 10px 0 0 0; font-size: 16px;">
                        Contraseña Actualizada Exitosamente
                    </p>
                </div>

                <!-- Body -->
                <div style="padding: 40px 30px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <div style="background-color: #d4edda; border-radius: 50%; width: 80px; height: 80px;
                                    margin: 0 auto; display: flex; align-items: center; justify-content: center;">
                            <span style="font-size: 40px;">✅</span>
                        </div>
                    </div>

                    <h2 style="color: #333333; margin: 0 0 20px 0; font-size: 24px; text-align: center;">
                        ¡Contraseña Actualizada!
                    </h2>

                    <p style="color: #555555; line-height: 1.6; margin: 0 0 20px 0; font-size: 16px;">
                        Hola,
                    </p>

                    <p style="color: #555555; line-height: 1.6; margin: 0 0 30px 0; font-size: 16px;">
                        Te confirmamos que la contraseña de tu cuenta en <strong>Pro Shooter API</strong>
                        ha sido actualizada exitosamente.
                    </p>

                    <!-- Security Alert -->
                    <div style="background-color: #e3f2fd; border-left: 4px solid #2196f3; padding: 20px; margin: 30px 0;">
                        <h3 style="color: #1565c0; margin: 0 0 15px 0; font-size: 18px;">
                            🔒 Aviso de Seguridad
                        </h3>
                        <p style="color: #1565c0; margin: 0; line-height: 1.6;">
                            Si <strong>NO</strong> realizaste este cambio, por favor contacta
                            inmediatamente con nuestro equipo de soporte.
                        </p>
                    </div>

                    <p style="color: #555555; line-height: 1.6; margin: 30px 0 0 0; font-size: 16px;">
                        Ya puedes iniciar sesión con tu nueva contraseña. ¡Gracias por mantener
                        tu cuenta segura!
                    </p>
                </div>

                <!-- Footer -->
                <div style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #dee2e6;">
                    <p style="color: #6c757d; margin: 0; font-size: 12px; line-height: 1.4;">
                        Este email fue enviado automáticamente por <strong>Pro Shooter API</strong>.<br>
                        No responder a este mensaje.
                    </p>
                    <p style="color: #6c757d; margin: 10px 0 0 0; font-size: 12px;">
                        © 2025 Pro Shooter API. Todos los derechos reservados.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        try:
            email_data = {
                "from": self.sender_email,
                "to": [recipient_email],
                "subject": "✅ Contraseña Actualizada - Pro Shooter API",
                "html": html_content,
            }

            response = resend.Emails.send(email_data)

            logger.info(
                f"✅ Notificación de cambio de contraseña enviada a {recipient_email}. ID: {response.get('id', 'unknown')}"
            )
            return True

        except Exception as e:
            logger.error(
                f"❌ Error al enviar notificación de cambio de contraseña: {str(e)}"
            )
            return False
