# src/infrastructure/services/email_service.py
"""Service d'envoi d'emails via SMTP."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dataclasses import dataclass
import os
import logging

logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    """Configuration SMTP."""
    host: str = "smtp.gmail.com"
    port: int = 587
    username: str = ""
    password: str = ""
    from_email: str = ""
    from_name: str = "ALVS - NarAction"
    use_tls: bool = True
    
    @classmethod
    def from_env(cls) -> 'EmailConfig':
        """Charge la config depuis les variables d'environnement."""
        return cls(
            host=os.getenv('SMTP_HOST', 'smtp.gmail.com'),
            port=int(os.getenv('SMTP_PORT', '587')),
            username=os.getenv('SMTP_USERNAME', ''),
            password=os.getenv('SMTP_PASSWORD', ''),
            from_email=os.getenv('SMTP_FROM_EMAIL', ''),
            from_name=os.getenv('SMTP_FROM_NAME', 'ALVS - NarAction'),
            use_tls=os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
        )


class EmailService:
    """
    Service d'envoi d'emails via SMTP.
    
    Utilise Gmail par defaut mais peut etre configure pour
    d'autres providers (SendGrid, Mailgun, etc.)
    """
    
    def __init__(self, config: Optional[EmailConfig] = None):
        self.config = config or EmailConfig.from_env()
        self._enabled = bool(self.config.username and self.config.password)
        
        if not self._enabled:
            logger.warning("SMTP non configure - les emails ne seront pas envoyes")
    
    def is_enabled(self) -> bool:
        """Verifie si le service email est configure."""
        return self._enabled
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None
    ) -> bool:
        """
        Envoie un email.
        
        Args:
            to_email: Adresse email du destinataire
            subject: Sujet de l'email
            body_html: Corps HTML de l'email
            body_text: Corps texte (optionnel, genere depuis HTML si absent)
            
        Returns:
            True si l'email a ete envoye, False sinon
        """
        if not self._enabled:
            logger.warning(f"Email non envoye (SMTP non configure): {subject} -> {to_email}")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.config.from_name} <{self.config.from_email}>"
            msg['To'] = to_email
            
            # Corps texte
            if body_text is None:
                # Convertir HTML en texte basique
                import re
                body_text = re.sub('<[^<]+?>', '', body_html)
            
            msg.attach(MIMEText(body_text, 'plain'))
            msg.attach(MIMEText(body_html, 'html'))
            
            # Connexion SMTP
            with smtplib.SMTP(self.config.host, self.config.port) as server:
                if self.config.use_tls:
                    server.starttls()
                server.login(self.config.username, self.config.password)
                server.sendmail(
                    self.config.from_email,
                    to_email,
                    msg.as_string()
                )
            
            logger.info(f"Email envoye: {subject} -> {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi email: {e}")
            return False
    
    def send_password_reset(self, to_email: str, reset_token: str, reset_url: str) -> bool:
        """Envoie un email de reinitialisation de mot de passe."""
        subject = "Reinitialisation de votre mot de passe - ALVS"
        
        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4A90A4; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background: #f9f9f9; }}
                .button {{ 
                    display: inline-block; 
                    padding: 12px 24px; 
                    background: #4A90A4; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                .code {{ 
                    font-family: monospace; 
                    background: #eee; 
                    padding: 10px; 
                    border-radius: 5px;
                    font-size: 16px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>ALVS - NarAction</h1>
                </div>
                <div class="content">
                    <h2>Reinitialisation de mot de passe</h2>
                    <p>Vous avez demande la reinitialisation de votre mot de passe.</p>
                    <p>Cliquez sur le bouton ci-dessous pour definir un nouveau mot de passe :</p>
                    <p style="text-align: center;">
                        <a href="{reset_url}" class="button">Reinitialiser mon mot de passe</a>
                    </p>
                    <p>Ou copiez ce code dans l'application :</p>
                    <p class="code">{reset_token}</p>
                    <p><strong>Ce lien expire dans 15 minutes.</strong></p>
                    <p>Si vous n'avez pas demande cette reinitialisation, ignorez cet email.</p>
                </div>
                <div class="footer">
                    <p>ALVS - Correspondances Litteraires Internationales</p>
                    <p>Cet email a ete envoye automatiquement, merci de ne pas y repondre.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body_html)


# Instance globale
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Retourne l'instance du service email."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
