# ALVS Backend API

API REST pour la plateforme **ALVS** (Aventure Litteraire Vers le Sud), une application de correspondances litteraires pour l'association **NarAction**. Le concept central est le **COLLI** (Communaute de Lectrices et Lecteurs Internationaux) : un club litteraire ou les membres echangent des lettres, commentent et sont geres via un workflow d'adhesion.

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Framework | Flask 3.0 |
| ORM | SQLAlchemy 2.0 + Alembic |
| Base de donnees | PostgreSQL 16 (prod) / SQLite (dev) |
| Authentification | Flask-JWT-Extended (access token + refresh cookie HttpOnly) |
| Hachage | bcrypt |
| Cache / Revocation tokens | Redis 7 |
| Temps reel | Flask-SocketIO (WebSocket) |
| Validation | Marshmallow + Pydantic |
| Injection de dependances | dependency-injector |
| Rate limiting | Flask-Limiter |
| Documentation API | Flasgger (Swagger UI) |
| Logging | structlog |
| Serveur WSGI | Gunicorn |

**Architecture** : Clean Architecture / DDD avec couches Domain, Application (Use Cases), Infrastructure.

## Fonctionnalites principales

- **Authentification** : register, login, refresh token, logout, forgot/reset password, change password
- **COLLIs** : CRUD, workflow d'approbation admin, adhesion avec approbation par le manager, invitations par lien
- **Lettres** : creation (texte ou fichier), CRUD, pagination
- **Commentaires** : CRUD sur les lettres
- **Notifications** : temps reel via Socket.IO
- **Administration** : gestion des utilisateurs, changement de roles, statistiques dashboard
- **Recherche globale** : recherche sur COLLIs, lettres et utilisateurs
- **RGPD** : export des donnees personnelles (Article 20), demande de suppression (Article 17)
- **Securite** : verrouillage de compte (5 tentatives / 15 min), audit logger, rate limiting

## Installation

### Developpement local

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements-dev.txt

cp .env.example .env
# Editer .env (au minimum SECRET_KEY et JWT_SECRET_KEY)

FLASK_ENV=development python -m src.infrastructure.web.app
```

L'application cree automatiquement les tables SQLite et un admin par defaut :
- Email : `admin@alvs.fr`
- Mot de passe : `Admin1234`

Swagger UI disponible sur `http://localhost:5000/docs`.

### Docker (stack complete)

```bash
docker-compose up --build
```

Lance 3 services : API Flask (port 5000), PostgreSQL 16, Redis 7.

### Production

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 "src.infrastructure.web.app:create_app()"
```

## Configuration (.env)

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///alvs.db
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000
REDIS_URL=redis://localhost:6379/0
CORS_ORIGIN=http://localhost:5173
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

Environnements disponibles via `FLASK_ENV` : `development` (SQLite, defaut), `testing` (SQLite in-memory), `production` (SECRET_KEY obligatoire, cookies HTTPS).

## Tests

```bash
# Tous les tests
pytest

# Par categorie
pytest tests/unit -m unit
pytest tests/integration -m integration

# Avec couverture
pytest --cov=src --cov-report=html
```

- Base de test : SQLite in-memory (aucune dependance externe)
- Markers : `unit`, `integration`, `e2e`, `slow`
- Fixtures : `client`, `auth_headers`, `admin_headers`, `registered_user`, `setup_colli`

## Structure du projet

```
src/
├── domain/                  # Entites, value objects, events (zero dependance externe)
│   ├── collaboration/       # Colli, Letter, Comment, Membership
│   ├── identity/            # User
│   └── notification/        # Notification
├── application/             # DTOs, use cases, interfaces
│   └── use_cases/           # colli/, comment/, letter/, user/
└── infrastructure/          # Implementation concrete
    ├── persistence/         # SQLAlchemy models, repositories, UoW
    ├── security/            # JWT, lockout, audit
    ├── services/            # email, notifications
    └── web/
        ├── app.py           # Flask factory
        ├── routes/          # 12 blueprints (auth, admin, collis, letters, ...)
        ├── middlewares/      # auth, error handler, rate limiter
        └── schemas/         # Marshmallow validation
```

## Routes API

Toutes les routes sont prefixees par `/api/v1/`. Voir la documentation Swagger a `/docs` pour le detail complet.

| Prefix | Description |
|--------|-------------|
| `/auth` | Authentification (login, register, refresh, logout, password) |
| `/admin` | Administration (users CRUD, stats) |
| `/collis` | COLLIs (CRUD, membership, approbation) |
| `/collis/:id/letters` | Lettres (CRUD) |
| `/collis/:id/invite` | Invitations par lien |
| `/search` | Recherche globale |
| `/export` | Export RGPD |
| `/health` | Health check |

## Migrations

```bash
alembic upgrade head                              # Appliquer les migrations
alembic revision --autogenerate -m "description"  # Creer une migration
```
