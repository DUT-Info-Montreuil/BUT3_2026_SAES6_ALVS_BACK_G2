# scripts/create_admin.py
"""Script pour créer un compte administrateur."""

import sys
import logging

sys.path.insert(0, '.')

from src.infrastructure.web.app import create_app
from src.infrastructure.container import Container
from src.domain.identity.entities.user import User
from src.domain.identity.value_objects.user_role import UserRole
from src.domain.identity.value_objects.hashed_password import HashedPassword
from uuid import uuid4


# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


def create_admin(email: str, password: str, first_name: str = "Admin", last_name: str = "ALVS"):
    """Crée un utilisateur avec le rôle ADMIN."""
    app = create_app()
    
    with app.app_context():
        container = Container()
        user_repo = container.user_repository()
        
        # Vérifier si l'email existe déjà
        existing = user_repo.find_by_email(email)
        if existing:
            logger.error(f"L'email {email} existe déjà !")
            return
        
        # Créer l'admin
        admin = User(
            id=uuid4(),
            email=email,
            password=HashedPassword.create(password),
            first_name=first_name,
            last_name=last_name,
            role=UserRole.ADMIN
        )
        
        user_repo.save(admin)
        logger.info(f"Admin créé avec succès - Email: {email}, Rôle: ADMIN")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Créer un compte administrateur")
    parser.add_argument("--email", required=True, help="Email de l'admin")
    parser.add_argument("--password", required=True, help="Mot de passe (min 8 caractères)")
    parser.add_argument("--first-name", default="Admin", help="Prénom")
    parser.add_argument("--last-name", default="ALVS", help="Nom")
    
    args = parser.parse_args()
    create_admin(args.email, args.password, args.first_name, args.last_name)
