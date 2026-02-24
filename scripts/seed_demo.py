#!/usr/bin/env python3
"""
Script de seed pour peupler le backend ALVS avec des données de démonstration.
Utilise directement le conteneur DI pour injecter dans les repos in-memory.

Usage:
    cd BUT3_2026_SAES6_ALVS_BACK_G2
    PYTHONPATH=. python scripts/seed_demo.py
"""

import sys
import logging

sys.path.insert(0, '.')

logging.basicConfig(level=logging.WARNING)

from uuid import uuid4
from src.infrastructure.web.app import create_app
from src.infrastructure.container import Container
from src.domain.identity.entities.user import User
from src.domain.identity.value_objects.user_role import UserRole
from src.domain.identity.value_objects.hashed_password import HashedPassword
from src.domain.identity.value_objects.email import Email
from src.domain.collaboration.entities.colli import Colli
from src.domain.collaboration.value_objects.colli_status import ColliStatus
from src.domain.collaboration.value_objects.member_role import MemberRole
from src.domain.collaboration.value_objects.letter_type import LetterType


# ==========================================
# Données de démonstration
# ==========================================

USERS_DATA = [
    ("admin@naraction.org", "AdminPassword123!", "Admin", "NarAction", UserRole.ADMIN),
    ("alice@naraction.org", "Password123!", "Alice", "Martin", UserRole.MEMBER),
    ("bob@naraction.org", "Password123!", "Bob", "Dupont", UserRole.MEMBER),
    ("claire@naraction.org", "Password123!", "Claire", "Bernard", UserRole.MEMBER),
    ("david@naraction.org", "Password123!", "David", "Leroy", UserRole.MEMBER),
    ("prof@naraction.org", "Password123!", "Marie", "Duval", UserRole.TEACHER),
]

COLLIS_DATA = [
    ("Les Voyageurs du Verbe", "Poesie contemporaine",
     "Un COLLI dedie a l'echange de poemes contemporains entre passionnes de la langue francaise."),
    ("Plumes Croisees", "Correspondance epistolaire",
     "Echangeons des lettres manuscrites dans la tradition des grands epistoliers."),
    ("L'Atelier des Mots", "Ecriture creative",
     "Un espace pour partager vos nouvelles, micro-fictions et exercices d'ecriture."),
]

LETTERS_DATA = [
    (0, 1, "Cher ami,\n\nLes mots sont comme des oiseaux migrateurs. Ils voyagent d'une ame a l'autre, portant avec eux la chaleur des terres traversees.\n\nVoici un poeme que j'ai ecrit ce matin :\n\nL'aube se leve, timide,\nSur les toits encore endormis.\nLes mots naissent, humides,\nDe la rosee de mes ecrits.\n\nQu'en pensez-vous ?\n\nAvec toute mon amitie,\nAlice"),
    (0, 2, "Chere Alice,\n\nVotre poeme m'a touche. Il y a dans vos vers une simplicite lumineuse.\n\nPermettez-moi de vous repondre avec ces quelques lignes :\n\nEntre les lignes du silence,\nLes mots dansent, legers,\nComme des feuilles d'automne\nQui refusent de tomber.\n\nAu plaisir de vous lire,\nBob"),
    (1, 3, "Cher correspondant,\n\nJe vous ecris depuis ma petite chambre, ou la pluie tambourine doucement contre les carreaux. C'est le temps ideal pour ecrire, ne trouvez-vous pas ?\n\nJ'ai toujours cru que les lettres avaient un pouvoir que les messages instantanes n'auront jamais : celui de faire voyager le lecteur dans le temps et l'espace.\n\nBien a vous,\nClaire"),
    (2, 4, "Bonjour a tous,\n\nVoici un exercice d'ecriture : decrire un souvenir d'enfance en exactement 100 mots.\n\nJe commence :\n\nLe grenier sentait la poussiere et les vieux livres. Grand-mere rangeait ses tresors dans des boites en carton. Un jour, j'en ai ouvert une. A l'interieur, des centaines de lettres jaunies, attachees par un ruban bleu. Les lettres de grand-pere, envoyees depuis l'autre bout du monde. J'ai lu la premiere, les mains tremblantes. Il y parlait d'un ciel si bleu qu'il aurait voulu le mettre en bouteille. Ce jour-la, j'ai compris que les mots pouvaient traverser le temps.\n\nA votre tour !\nDavid"),
]

COMMENTS_DATA = [
    # (letter_index, user_index, content)
    (0, 2, "Magnifique poeme Alice ! L'image des oiseaux migrateurs est tres evocatrice."),
    (0, 3, "J'adore la musicalite de vos vers. Continuez !"),
    (1, 1, "Merci Bob, vos mots sur les feuilles d'automne sont splendides."),
    (3, 1, "Quel bel exercice ! Votre texte sur le grenier m'a donne des frissons."),
    (3, 5, "Tres belle initiative David. Je propose le meme exercice en classe la semaine prochaine."),
]


def main():
    print("=" * 60)
    print("  ALVS - Seed de donnees de demonstration")
    print("=" * 60)

    app = create_app()

    with app.app_context():
        container = Container()
        user_repo = container.user_repository()
        colli_repo = container.colli_repository()
        letter_repo = container.letter_repository()
        comment_repo = container.comment_repository()

        # ==========================================
        # 1. Creer les utilisateurs
        # ==========================================
        print("\n[1/5] Creation des utilisateurs...")
        users = []
        for email_str, password, first_name, last_name, role in USERS_DATA:
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
            role_label = role.value if hasattr(role, 'value') else str(role)
            print(f"  + {first_name} {last_name} ({email_str}) [{role_label}]")

        admin = users[0]
        prof = users[5]

        # ==========================================
        # 2. Creer les COLLIs (par le prof)
        # ==========================================
        print("\n[2/5] Creation des COLLIs...")
        collis = []
        for name, theme, description in COLLIS_DATA:
            colli = Colli(
                id=uuid4(),
                name=name,
                theme=theme,
                description=description,
                creator_id=prof.id,
                status=ColliStatus.PENDING,
            )
            colli_repo.save(colli)
            collis.append(colli)
            print(f"  + \"{name}\" (theme: {theme})")

        # ==========================================
        # 3. Approuver et ajouter les membres
        # ==========================================
        print("\n[3/5] Approbation et ajout des membres...")
        for colli in collis:
            # Approuver (approve() adds creator as manager automatically)
            colli.approve(approved_by=admin.id)

            # Ajouter les membres (users index 1-4 = alice, bob, claire, david)
            for user in users[1:5]:
                colli.add_member(user.id, MemberRole.MEMBER)
            colli_repo.save(colli)
            print(f"  + \"{colli.name}\" approuve, {len(colli.members)} membres")

        # ==========================================
        # 4. Creer les lettres
        # ==========================================
        print("\n[4/5] Creation des lettres...")
        from src.domain.collaboration.entities.letter import Letter

        letters = []
        for colli_idx, user_idx, content in LETTERS_DATA:
            letter = Letter(
                id=uuid4(),
                letter_type=LetterType.TEXT,
                colli_id=collis[colli_idx].id,
                sender_id=users[user_idx].id,
                content=content,
            )
            letter_repo.save(letter)
            letters.append(letter)
            sender = users[user_idx]
            print(f"  + Lettre de {sender.first_name} dans \"{collis[colli_idx].name}\"")

        # ==========================================
        # 5. Creer les commentaires
        # ==========================================
        print("\n[5/5] Creation des commentaires...")
        from src.domain.collaboration.entities.comment import Comment

        for letter_idx, user_idx, content in COMMENTS_DATA:
            comment = Comment(
                id=uuid4(),
                letter_id=letters[letter_idx].id,
                sender_id=users[user_idx].id,
                content=content,
            )
            comment_repo.save(comment)
            sender = users[user_idx]
            print(f"  + Commentaire de {sender.first_name} sur lettre {letter_idx + 1}")

    # ==========================================
    # Resume
    # ==========================================
    print("\n" + "=" * 60)
    print("  SEED TERMINE !")
    print("=" * 60)
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
    print("  3 COLLIs crees, approuves, avec 4 membres chacun")
    print("  4 lettres et 5 commentaires")
    print()
    print("  Frontend: http://localhost:5173")
    print("  Backend:  http://localhost:5000")
    print("  API Docs: http://localhost:5000/docs")
    print()


if __name__ == "__main__":
    main()
