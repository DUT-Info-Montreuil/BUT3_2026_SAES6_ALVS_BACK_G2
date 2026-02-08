# Configuration Swagger/OpenAPI pour l'API ALVS

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs/",
}

SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "ALVS API",
        "description": "API pour ALVS - Aventure Littéraire Vers le Sud. Plateforme de correspondance littéraire.",
        "version": "1.0.0",
        "contact": {
            "name": "Équipe ALVS",
        },
    },
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header. Exemple: 'Bearer {token}'",
        }
    },
    "tags": [
        {"name": "Users", "description": "Gestion des utilisateurs"},
        {"name": "Collis", "description": "Gestion des COLLIs (Communautés)"},
        {"name": "Members", "description": "Gestion des membres de COLLI"},
        {"name": "Letters", "description": "Gestion des lettres"},
        {"name": "Comments", "description": "Gestion des commentaires"},
    ],
}
