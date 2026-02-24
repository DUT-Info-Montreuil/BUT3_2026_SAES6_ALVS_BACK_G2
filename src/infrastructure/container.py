# src/infrastructure/container.py
"""
Container d'injection de dépendances.

Utilise dependency-injector pour le wiring automatique des dépendances
selon les principes de Clean Architecture.
"""

from dependency_injector import containers, providers

# Configuration
from src.infrastructure.config.settings import Settings, get_settings

# Repositories (interfaces)
from src.domain.collaboration.repositories.colli_repository import IColliRepository

# Use Cases
from src.application.use_cases.colli.create_colli import CreateColliUseCase
from src.application.use_cases.colli.approve_colli import ApproveColliUseCase

# Services
from src.infrastructure.security.jwt_service import JWTService
from src.application.interfaces.event_publisher import IEventPublisher


class Container(containers.DeclarativeContainer):
    """
    Container principal d'injection de dépendances.
    
    Organisation:
    - config: Configuration de l'application
    - gateways: Connexions aux services externes (DB, Redis, etc.)
    - repositories: Implémentations des repositories
    - services: Services métier
    - use_cases: Cas d'utilisation de l'application
    """
    
    # =========================================================================
    # CONFIGURATION
    # =========================================================================
    
    config = providers.Singleton(get_settings)
    
    # =========================================================================
    # GATEWAYS (connexions externes)
    # =========================================================================
    
    # Database session factory
    # db_session_factory = providers.Singleton(
    #     create_session_factory,
    #     database_url=config.provided.DATABASE_URL
    # )
    
    # Redis client (optionnel)
    # redis_client = providers.Singleton(
    #     create_redis_client,
    #     redis_url=config.provided.REDIS_URL
    # )
    
    # =========================================================================
    # REPOSITORIES
    # =========================================================================
    
    # Repository In-Memory (pour dev/tests)
    colli_repository = providers.Singleton(
        "src.infrastructure.persistence.in_memory.colli_repository.InMemoryColliRepository"
    )
    
    user_repository = providers.Singleton(
        "src.infrastructure.persistence.in_memory.user_repository.InMemoryUserRepository"
    )
    
    letter_repository = providers.Singleton(
        "src.infrastructure.persistence.in_memory.letter_repository.InMemoryLetterRepository"
    )
    
    comment_repository = providers.Singleton(
        "src.infrastructure.persistence.in_memory.comment_repository.InMemoryCommentRepository"
    )
    
    notification_repository = providers.Singleton(
        "src.infrastructure.persistence.in_memory.notification_repository.InMemoryNotificationRepository"
    )
    
    # Repository SQLAlchemy (pour production)
    # colli_repository = providers.Singleton(
    #     SQLAlchemyColliRepository,
    #     session_factory=db_session_factory
    # )
    
    # =========================================================================
    # SERVICES
    # =========================================================================
    
    jwt_service = providers.Factory(
        JWTService,
        access_expires=config.provided.JWT_ACCESS_TOKEN_EXPIRES,
        refresh_expires=config.provided.JWT_REFRESH_TOKEN_EXPIRES
    )
    
    # Event Publisher (In-Memory pour dev/tests)
    event_publisher = providers.Singleton(
        "src.infrastructure.event_handlers.in_memory_publisher.InMemoryEventPublisher"
    )
    
    # =========================================================================
    # USE CASES
    # =========================================================================
    
    # Colli Use Cases
    create_colli_use_case = providers.Factory(
        CreateColliUseCase,
        colli_repository=colli_repository
    )
    
    approve_colli_use_case = providers.Factory(
        ApproveColliUseCase,
        colli_repository=colli_repository,
        event_publisher=event_publisher
    )
    
    get_colli_use_case = providers.Factory(
        "src.application.use_cases.colli.get_colli.GetColliByIdUseCase",
        colli_repository=colli_repository
    )
    
    list_collis_use_case = providers.Factory(
        "src.application.use_cases.colli.get_colli.ListCollisUseCase",
        colli_repository=colli_repository
    )
    
    delete_colli_use_case = providers.Factory(
        "src.application.use_cases.colli.delete_colli.DeleteColliUseCase",
        colli_repository=colli_repository
    )
    
    join_colli_use_case = providers.Factory(
        "src.application.use_cases.colli.membership.JoinColliUseCase",
        colli_repository=colli_repository
    )
    
    leave_colli_use_case = providers.Factory(
        "src.application.use_cases.colli.membership.LeaveColliUseCase",
        colli_repository=colli_repository
    )

    accept_member_use_case = providers.Factory(
        "src.application.use_cases.colli.membership.AcceptMemberUseCase",
        colli_repository=colli_repository
    )

    reject_member_use_case = providers.Factory(
        "src.application.use_cases.colli.membership.RejectMemberUseCase",
        colli_repository=colli_repository
    )

    list_members_use_case = providers.Factory(
        "src.application.use_cases.colli.list_members.ListMembersUseCase",
        colli_repository=colli_repository
    )
    
    update_colli_use_case = providers.Factory(
        "src.application.use_cases.colli.update_colli.UpdateColliUseCase",
        colli_repository=colli_repository
    )
    
    reject_colli_use_case = providers.Factory(
        "src.application.use_cases.colli.reject_colli.RejectColliUseCase",
        colli_repository=colli_repository
    )
    
    get_user_collis_use_case = providers.Factory(
        "src.application.use_cases.colli.get_user_collis.GetUserCollisUseCase",
        colli_repository=colli_repository
    )
    
    # User Use Cases
    register_user_use_case = providers.Factory(
        "src.application.use_cases.user.register_user.RegisterUserUseCase",
        user_repository=user_repository
    )
    
    authenticate_user_use_case = providers.Factory(
        "src.application.use_cases.user.authenticate_user.AuthenticateUserUseCase",
        user_repository=user_repository,
        jwt_service=jwt_service
    )
    
    get_current_user_use_case = providers.Factory(
        "src.application.use_cases.user.get_current_user.GetCurrentUserUseCase",
        user_repository=user_repository
    )
    
    update_profile_use_case = providers.Factory(
        "src.application.use_cases.user.update_profile.UpdateUserProfileUseCase",
        user_repository=user_repository
    )
    
    change_password_use_case = providers.Factory(
        "src.application.use_cases.user.change_password.ChangePasswordUseCase",
        user_repository=user_repository
    )
    
    # Letter Use Cases
    create_text_letter_use_case = providers.Factory(
        "src.application.use_cases.letter.create_letter.CreateTextLetterUseCase",
        letter_repository=letter_repository,
        colli_repository=colli_repository
    )
    
    create_file_letter_use_case = providers.Factory(
        "src.application.use_cases.letter.create_letter.CreateFileLetterUseCase",
        letter_repository=letter_repository,
        colli_repository=colli_repository
    )
    
    get_letters_use_case = providers.Factory(
        "src.application.use_cases.letter.get_letters.GetLettersForColliUseCase",
        letter_repository=letter_repository,
        comment_repository=comment_repository,
        colli_repository=colli_repository
    )
    
    get_letter_use_case = providers.Factory(
        "src.application.use_cases.letter.get_letters.GetLetterByIdUseCase",
        letter_repository=letter_repository,
        comment_repository=comment_repository,
        colli_repository=colli_repository
    )
    
    delete_letter_use_case = providers.Factory(
        "src.application.use_cases.letter.delete_letter.DeleteLetterUseCase",
        letter_repository=letter_repository,
        colli_repository=colli_repository
    )
    
    update_letter_use_case = providers.Factory(
        "src.application.use_cases.letter.update_letter.UpdateLetterUseCase",
        letter_repository=letter_repository
    )
    
    # Comment Use Cases
    create_comment_use_case = providers.Factory(
        "src.application.use_cases.comment.create_comment.CreateCommentUseCase",
        comment_repository=comment_repository,
        letter_repository=letter_repository,
        colli_repository=colli_repository
    )
    
    get_comments_use_case = providers.Factory(
        "src.application.use_cases.comment.get_comments.GetCommentsForLetterUseCase",
        comment_repository=comment_repository,
        letter_repository=letter_repository,
        colli_repository=colli_repository
    )
    
    delete_comment_use_case = providers.Factory(
        "src.application.use_cases.comment.delete_comment.DeleteCommentUseCase",
        comment_repository=comment_repository,
        letter_repository=letter_repository,
        colli_repository=colli_repository
    )
    
    update_comment_use_case = providers.Factory(
        "src.application.use_cases.comment.update_comment.UpdateCommentUseCase",
        comment_repository=comment_repository
    )



# Instance globale du container
container = Container()


def get_container() -> Container:
    """Récupère l'instance du container."""
    return container


def init_container(app=None) -> Container:
    """
    Initialise le container avec l'application Flask.
    
    Args:
        app: Instance Flask optionnelle.
        
    Returns:
        Container: Le container initialisé.
    """
    # Wire le container avec les modules qui l'utilisent
    container.wire(modules=[
        "src.infrastructure.web.routes.colli_routes",
        "src.infrastructure.web.routes.auth_routes",
        "src.infrastructure.web.routes.letter_routes",
        "src.infrastructure.web.routes.comment_routes",
        "src.infrastructure.web.routes.admin_routes",
        "src.infrastructure.web.routes.notification_routes",
        "src.infrastructure.web.routes.search_routes",
        "src.infrastructure.web.routes.export_routes",
    ])
    
    return container
