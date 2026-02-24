#!/usr/bin/env python3
"""
Lance le backend ALVS avec des données de démonstration pré-chargées.
Les repos in-memory sont peuplés avant de démarrer le serveur.

Usage:
    cd BUT3_2026_SAES6_ALVS_BACK_G2
    PYTHONPATH=. python scripts/seed_and_serve.py
"""

import sys
import logging

sys.path.insert(0, '.')

logging.basicConfig(level=logging.WARNING)

from uuid import uuid4
from src.infrastructure.web.app import create_app
from src.infrastructure.container import get_container
from src.domain.identity.entities.user import User
from src.domain.identity.value_objects.user_role import UserRole
from src.domain.identity.value_objects.hashed_password import HashedPassword
from src.domain.identity.value_objects.email import Email
from src.domain.collaboration.entities.colli import Colli
from src.domain.collaboration.entities.letter import Letter
from src.domain.collaboration.entities.comment import Comment
from src.domain.collaboration.value_objects.colli_status import ColliStatus
from src.domain.collaboration.value_objects.member_role import MemberRole
from src.domain.collaboration.value_objects.letter_type import LetterType


def seed_data(app):
    """Peuple les repos in-memory avec des données de demo."""
    with app.app_context():
        container = get_container()
        user_repo = container.user_repository()
        colli_repo = container.colli_repository()
        letter_repo = container.letter_repository()
        comment_repo = container.comment_repository()

        # ==========================================
        # Utilisateurs
        # ==========================================
        print("\n  [Seed] Creation des utilisateurs...")
        users_data = [
            ("admin@naraction.org", "AdminPassword123!", "Admin", "NarAction", UserRole.ADMIN),
            ("alice@naraction.org", "Password123!", "Alice", "Martin", UserRole.MEMBER),
            ("bob@naraction.org", "Password123!", "Bob", "Dupont", UserRole.MEMBER),
            ("claire@naraction.org", "Password123!", "Claire", "Bernard", UserRole.MEMBER),
            ("david@naraction.org", "Password123!", "David", "Leroy", UserRole.MEMBER),
            ("prof@naraction.org", "Password123!", "Marie", "Duval", UserRole.TEACHER),
        ]

        users = []
        for email_str, password, first_name, last_name, role in users_data:
            user = User(
                id=uuid4(),
                email=Email.create(email_str),
                password=HashedPassword.create(password),
                first_name=first_name,
                last_name=last_name,
                role=role,
            )
            user_repo.save(user)
            users.append(user)
            print(f"    + {first_name} {last_name} ({email_str}) [{role.value}]")

        admin = users[0]
        prof = users[5]

        # ==========================================
        # COLLIs
        # ==========================================
        print("\n  [Seed] Creation des COLLIs...")
        collis_data = [
            ("Les Voyageurs du Verbe", "Poesie contemporaine",
             "Un COLLI dedie a l'echange de poemes contemporains entre passionnes de la langue francaise."),
            ("Plumes Croisees", "Correspondance epistolaire",
             "Echangeons des lettres manuscrites dans la tradition des grands epistoliers."),
            ("L'Atelier des Mots", "Ecriture creative",
             "Un espace pour partager vos nouvelles, micro-fictions et exercices d'ecriture."),
        ]

        collis = []
        for name, theme, description in collis_data:
            colli = Colli.create(
                name=name,
                theme=theme,
                creator_id=prof.id,
                description=description,
            )
            # Approve + add members
            colli.approve(approved_by=admin.id)
            for user in users[1:5]:
                colli.add_member(user.id, MemberRole.MEMBER)
            colli_repo.save(colli)
            collis.append(colli)
            print(f"    + \"{name}\" ({len(colli.members)} membres)")

        # ==========================================
        # Lettres
        # ==========================================
        print("\n  [Seed] Creation des lettres...")
        letters_content = [
            (0, 1, "Cher ami,\n\nLes mots sont comme des oiseaux migrateurs. Ils voyagent d'une ame a l'autre, portant avec eux la chaleur des terres traversees.\n\nVoici un poeme que j'ai ecrit ce matin :\n\nL'aube se leve, timide,\nSur les toits encore endormis.\nLes mots naissent, humides,\nDe la rosee de mes ecrits.\n\nQu'en pensez-vous ?\n\nAvec toute mon amitie,\nAlice"),
            (0, 2, "Chere Alice,\n\nVotre poeme m'a touche. Il y a dans vos vers une simplicite lumineuse.\n\nPermettez-moi de vous repondre avec ces quelques lignes :\n\nEntre les lignes du silence,\nLes mots dansent, legers,\nComme des feuilles d'automne\nQui refusent de tomber.\n\nAu plaisir de vous lire,\nBob"),
            (1, 3, "Cher correspondant,\n\nJe vous ecris depuis ma petite chambre, ou la pluie tambourine doucement contre les carreaux. C'est le temps ideal pour ecrire, ne trouvez-vous pas ?\n\nJ'ai toujours cru que les lettres avaient un pouvoir que les messages instantanes n'auront jamais : celui de faire voyager le lecteur dans le temps et l'espace.\n\nBien a vous,\nClaire"),
            (2, 4, "Bonjour a tous,\n\nVoici un exercice d'ecriture : decrire un souvenir d'enfance en exactement 100 mots.\n\nLe grenier sentait la poussiere et les vieux livres. Grand-mere rangeait ses tresors dans des boites en carton. Un jour, j'en ai ouvert une. A l'interieur, des centaines de lettres jaunies, attachees par un ruban bleu. Les lettres de grand-pere, envoyees depuis l'autre bout du monde. J'ai lu la premiere, les mains tremblantes. Il y parlait d'un ciel si bleu qu'il aurait voulu le mettre en bouteille. Ce jour-la, j'ai compris que les mots pouvaient traverser le temps.\n\nA votre tour !\nDavid"),
        ]

        letters = []
        for colli_idx, user_idx, content in letters_content:
            letter = Letter(
                id=uuid4(),
                letter_type=LetterType.TEXT,
                colli_id=collis[colli_idx].id,
                sender_id=users[user_idx].id,
                content=content,
            )
            letter_repo.save(letter)
            letters.append(letter)
            print(f"    + Lettre de {users[user_idx].first_name} dans \"{collis[colli_idx].name}\"")

        # ==========================================
        # Commentaires
        # ==========================================
        print("\n  [Seed] Creation des commentaires...")
        comments_data = [
            (0, 2, "Magnifique poeme Alice ! L'image des oiseaux migrateurs est tres evocatrice."),
            (0, 3, "J'adore la musicalite de vos vers. Continuez !"),
            (1, 1, "Merci Bob, vos mots sur les feuilles d'automne sont splendides."),
            (3, 1, "Quel bel exercice ! Votre texte sur le grenier m'a donne des frissons."),
            (3, 5, "Tres belle initiative David. Je propose le meme exercice en classe la semaine prochaine."),
        ]

        for letter_idx, user_idx, content in comments_data:
            comment = Comment(
                id=uuid4(),
                letter_id=letters[letter_idx].id,
                sender_id=users[user_idx].id,
                content=content,
            )
            comment_repo.save(comment)
            print(f"    + Commentaire de {users[user_idx].first_name}")

        print("\n  [Seed] Termine ! 6 utilisateurs, 3 COLLIs, 4 lettres, 5 commentaires")


def main():
    print("=" * 60)
    print("  ALVS Backend - Demarrage avec donnees de demo")
    print("=" * 60)

    # Creer l'application Flask
    app = create_app()

    # Injecter les donnees de demo
    seed_data(app)

    # Afficher les comptes
    print()
    print("  Comptes de demo :")
    print("  -----------------------------------------------")
    print("  Admin:   admin@naraction.org  / AdminPassword123!")
    print("  Prof:    prof@naraction.org   / Password123!")
    print("  Alice:   alice@naraction.org  / Password123!")
    print("  Bob:     bob@naraction.org    / Password123!")
    print("  Claire:  claire@naraction.org / Password123!")
    print("  David:   david@naraction.org  / Password123!")
    print()
    print("  Frontend: http://localhost:5173")
    print("  Backend:  http://localhost:5000")
    print("  API Docs: http://localhost:5000/docs")
    print("=" * 60)

    # Demarrer le serveur avec SocketIO
    from src.infrastructure.websocket import init_socketio
    socketio = init_socketio(app)
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    main()
