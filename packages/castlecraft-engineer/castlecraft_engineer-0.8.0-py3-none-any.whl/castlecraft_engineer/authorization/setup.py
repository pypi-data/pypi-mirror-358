import logging
import os

import punq

from castlecraft_engineer.authorization.base_service import AuthorizationService
from castlecraft_engineer.authorization.default_services import (
    AllowAllAuthorizationService,
    DenyAllAuthorizationService,
)
from castlecraft_engineer.common.env import (
    AUTH_ENGINE_ALLOW,
    AUTH_ENGINE_DENY,
    ENV_AUTHORIZATION_ENGINE,
)

logger = logging.getLogger(__name__)


def setup_authorization(container: punq.Container):
    """
    Sets up the authorization service
    based on environment configuration
    and registers it with the provided DI container.
    """

    auth_engine_name = os.environ.get(
        ENV_AUTHORIZATION_ENGINE,
        AUTH_ENGINE_DENY,
    )
    auth_service_instance: AuthorizationService | None = None

    logger.info(
        "Attempting to configure authorization engine: "  # noqa: E501
        f"'{auth_engine_name}'",
    )

    if auth_engine_name == AUTH_ENGINE_ALLOW:
        try:
            logger.warning(
                "Configuring AllowAllAuthorizationService. Use with caution!",
            )
            auth_service_instance = AllowAllAuthorizationService()
        except Exception as e:
            logger.critical(
                f"Failed to instantiate AllowAllAuthorizationService: {e}. "
                "Defaulting to DenyAllAuthorizationService due to critical error."
            )
            auth_service_instance = DenyAllAuthorizationService()
    elif auth_engine_name == AUTH_ENGINE_DENY:
        try:
            logger.info("Configuring DenyAllAuthorizationService.")
            auth_service_instance = DenyAllAuthorizationService()
        except Exception as e:
            logger.critical(
                f"Failed to instantiate DenyAllAuthorizationService: {e}. "
                "Defaulting to DenyAllAuthorizationService due to critical error."
            )
            auth_service_instance = None
    else:
        logger.info(
            f"Attempting to use custom pre-configured AuthorizationService for engine '{auth_engine_name}'."  # noqa: E501
        )
        try:
            auth_service_instance = container.resolve(AuthorizationService)
            logger.info(
                f"Successfully resolved pre-configured custom AuthorizationService: {auth_service_instance.__class__.__name__}"  # noqa: E501
            )
        except punq.MissingDependencyError:
            logger.error(
                f"Custom engine '{auth_engine_name}' selected, but no AuthorizationService "  # noqa: E501
                "found pre-registered in DI container. Ensure it's configured and registered by the application. Falling back."  # noqa: E501
            )
            auth_service_instance = None
        except Exception as e:
            logger.exception(
                f"An unexpected error occurred while trying to resolve custom AuthorizationService for engine '{auth_engine_name}': {e}. Falling back."  # noqa: E501
            )
            auth_service_instance = None

    # Fallback Section
    if auth_service_instance is None:
        logger.critical(
            "Authorization service could not be initialized as configured. "
            "Attempting to use DenyAllAuthorizationService as a final fallback."
        )
        try:
            auth_service_instance = DenyAllAuthorizationService()  # Final attempt
        except Exception as e:
            logger.critical(
                f"CRITICAL FAILURE: Could not instantiate even the final fallback "
                f"DenyAllAuthorizationService: {e}. Authorization will not be configured."
            )
            auth_service_instance = None

    if auth_service_instance:
        container.register(
            AuthorizationService,
            instance=auth_service_instance,
            scope=punq.Scope.singleton,
        )
        logger.info(
            "Registered AuthorizationService:"
            f" {auth_service_instance.__class__.__name__}"
        )
    else:
        logger.error(
            "CRITICAL: Could not determine or initialize "
            "any authorization service, including fallback!"
        )
