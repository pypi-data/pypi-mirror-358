import functools
import inspect
import logging
from typing import TYPE_CHECKING, Any, Optional

import punq  # type: ignore

if TYPE_CHECKING:  # pragma: no cover
    # These imports are only for type checking and will not cause circular imports at runtime
    from castlecraft_engineer.abstractions.command_bus import CommandBus
    from castlecraft_engineer.abstractions.event_bus import EventBus
    from castlecraft_engineer.abstractions.query_bus import QueryBus

logger = logging.getLogger(__name__)


class ContainerBuilder:
    """
    Builds the DI container progressively.
    """

    def __init__(self) -> None:
        self._logger = logger
        self._container = punq.Container()
        self._db_registered = False
        self._async_db_registered = False
        self._cache_registered = False
        self._async_cache_registered = False
        self._authentication_registered = False
        self._command_bus_registered = False
        self._query_bus_registered = False
        self._event_bus_registered = False
        self._authorization_registered = False
        self.command_bus: Optional["CommandBus"] = None
        self.query_bus: Optional["QueryBus"] = None
        self.event_bus: Optional["EventBus"] = None
        self._container.register(punq.Container, instance=self._container)
        self._logger.info("Initialized ContainerBuilder.")

    def with_database(self) -> "ContainerBuilder":
        """
        Registers database connection and components
        """
        if self._db_registered:
            self._logger.warning(
                "Database components already registered. Skipping.",
            )
            return self

        self._logger.info("Registering synchronous database components...")

        try:
            from sqlalchemy import Engine
            from sqlalchemy.orm import Session, sessionmaker

            from castlecraft_engineer.database.connection import (
                SyncSessionFactory,
                get_engine,
            )

            sync_engine = get_engine()
            self._container.register(
                Engine,
                instance=sync_engine,
                name="db_sync_engine",
            )

            self._container.register(
                sessionmaker[Session],
                instance=SyncSessionFactory,
                name="db_sync_session_factory",
            )

            self._container.register(
                Session,
                factory=lambda: SyncSessionFactory(),
            )

            self._db_registered = True
            self._logger.info("Synchronous database components registered.")
        except Exception as e:
            self._logger.error(
                f"Failed to register synchronous database components: {e}",
                exc_info=True,
            )

        return self

    def with_async_database(self) -> "ContainerBuilder":
        """
        Registers asynchronous database
        connection and components.
        """
        if self._async_db_registered:
            self._logger.warning(
                "Asynchronous database components already registered. Skipping.",  # noqa: E501
            )
            return self

        self._logger.info("Registering asynchronous database components...")

        try:
            from sqlalchemy.ext.asyncio import (
                AsyncEngine,
                AsyncSession,
                async_sessionmaker,
            )

            from castlecraft_engineer.database.connection import (
                AsyncSessionFactory,
                get_async_engine,
            )

            async_engine = get_async_engine()
            self._container.register(
                AsyncEngine, instance=async_engine, name="db_async_engine"
            )

            self._container.register(
                async_sessionmaker[AsyncSession],
                instance=AsyncSessionFactory,
                name="db_async_session_factory",
            )

            self._container.register(
                AsyncSession, factory=lambda: AsyncSessionFactory()
            )

            self._async_db_registered = True
            self._logger.info("Asynchronous database components registered.")
        except Exception as e:
            self._logger.error(
                f"Failed to register asynchronous database components: {e}",
                exc_info=True,
            )

        return self

    def with_cache(self, is_async: bool = False) -> "ContainerBuilder":
        """
        Registers Cache connection and components.

        Args:
            is_async: If True, registers the asynchronous Redis client.
                      If False (default), registers the synchronous client.
        """
        if is_async and self._async_cache_registered:
            self._logger.warning(
                "Asynchronous cache components already registered. Skipping.",
            )
            return self
        if not is_async and self._cache_registered:
            self._logger.warning(
                "Synchronous cache components already registered. Skipping.",
            )
            return self

        if is_async:
            self._logger.info(
                "Registering asynchronous cache components...",
            )

            try:
                import redis.asyncio as aredis

                from castlecraft_engineer.caching.cache import (
                    get_redis_cache_async_connection,
                )

                # Safer: Register a factory
                self._container.register(
                    aredis.Redis,
                    factory=lambda **_: get_redis_cache_async_connection(),
                    scope=punq.Scope.singleton,
                    name="cache_async",
                )
                self._async_cache_registered = True
                self._logger.info(
                    "Asynchronous cache components registered (factory).",
                )
            except Exception as e:
                self._logger.error(
                    f"Failed to register asynchronous cache components: {e}",
                    exc_info=True,
                )
        else:
            self._logger.info("Registering synchronous cache components...")
            try:
                import redis

                from castlecraft_engineer.caching.cache import (
                    get_redis_cache_connection,
                )

                sync_cache_client = get_redis_cache_connection()
                self._container.register(
                    redis.Redis, instance=sync_cache_client, name="cache_sync"
                )
                self._cache_registered = True
                self._logger.info("Synchronous cache components registered.")
            except Exception as e:
                self._logger.error(
                    f"Failed to register synchronous cache components: {e}",
                    exc_info=True,
                )

        return self

    def with_authentication(self) -> "ContainerBuilder":
        """
        Registers Authentication connection and components
        """
        if self._authentication_registered:
            self._logger.warning(
                "Authentication components already registered. Skipping.",
            )
            return self

        self._logger.info(
            "Registering Authentication components (AuthenticationService)...",
        )

        try:
            from castlecraft_engineer.application.auth import AuthenticationService

            # Prefer async if registered, otherwise use sync if registered
            def auth_service_factory(
                container=self._container,
            ):
                sync_cache = None
                async_cache = None
                if self._async_cache_registered:
                    try:
                        import redis.asyncio as aredis

                        # Resolve the async client (trigger factory)
                        async_cache = container.resolve(
                            aredis.Redis,
                            name="cache_async",
                        )
                        self._logger.info(
                            "AuthenticationService will use asynchronous cache.",
                        )
                    except ImportError:
                        self._logger.info(
                            "aredis library not found for auth_service_factory. Async cache will not be used."  # noqa: E501
                        )
                    except Exception as e:
                        self._logger.error(
                            f"Failed to resolve async cache for AuthenticationService: {e}"
                        )
                if not async_cache and self._cache_registered:
                    try:
                        import redis

                        sync_cache = container.resolve(
                            redis.Redis,
                            name="cache_sync",
                        )
                        self._logger.info(
                            "AuthenticationService will use synchronous cache.",
                        )
                    except ImportError:
                        self._logger.info(
                            "redis library not found for auth_service_factory. Sync cache will not be used."  # noqa: E501
                        )
                    except Exception as e:
                        self._logger.error(
                            f"Failed to resolve sync cache for AuthenticationService: {e}"
                        )

                return AuthenticationService(
                    cache_client=sync_cache, async_cache_client=async_cache
                )

            self._container.register(
                AuthenticationService,
                factory=auth_service_factory,
                scope=punq.Scope.singleton,
            )
            self._authentication_registered = True
            self._logger.info("Authentication components registered.")
        except Exception as e:
            self._logger.error(
                f"Failed to register Authentication components: {e}",
                exc_info=True,
            )

        return self

    def with_command_bus(self) -> "ContainerBuilder":
        """Registers the CommandBus as a singleton."""
        if self._command_bus_registered:
            self._logger.warning("CommandBus already registered. Skipping.")
            return self

        self._logger.info("Registering CommandBus...")
        try:
            from castlecraft_engineer.abstractions.command_bus import CommandBus

            self._container.register(
                CommandBus,
                factory=lambda c=self._container: CommandBus(container=c),
                scope=punq.Scope.singleton,
            )
            self._command_bus_registered = True
            self.command_bus = self._container.resolve(CommandBus)
            self._logger.info("CommandBus registered as singleton.")
        except Exception as e:
            self._logger.error(f"Failed to register CommandBus: {e}", exc_info=True)
        return self

    def with_query_bus(self) -> "ContainerBuilder":
        """Registers the QueryBus as a singleton."""
        if self._query_bus_registered:
            self._logger.warning("QueryBus already registered. Skipping.")
            return self

        self._logger.info("Registering QueryBus...")
        try:
            from castlecraft_engineer.abstractions.query_bus import QueryBus

            self._container.register(
                QueryBus,
                factory=lambda c=self._container: QueryBus(container=c),
                scope=punq.Scope.singleton,
            )
            self._query_bus_registered = True
            self.query_bus = self._container.resolve(QueryBus)
            self._logger.info("QueryBus registered as singleton.")
        except Exception as e:
            self._logger.error(f"Failed to register QueryBus: {e}", exc_info=True)
        return self

    def with_event_bus(self) -> "ContainerBuilder":
        """
        Registers the EventBus as a singleton.
        Note: Event handlers are typically registered directly with the
        EventBus instance after it's resolved, not via the DI container
        for the handlers themselves unless the EventBus is modified to
        resolve handlers.
        """
        if self._event_bus_registered:
            self._logger.warning("EventBus already registered. Skipping.")
            return self

        self._logger.info("Registering EventBus...")
        try:
            from castlecraft_engineer.abstractions.event_bus import EventBus

            self._container.register(
                EventBus,
                factory=lambda c=self._container: EventBus(container=c),
                scope=punq.Scope.singleton,
            )
            self._event_bus_registered = True
            self.event_bus = self._container.resolve(EventBus)
            self._logger.info("EventBus registered as singleton.")
        except Exception as e:
            self._logger.error(f"Failed to register EventBus: {e}", exc_info=True)
        return self

    def with_authorization(self) -> "ContainerBuilder":
        """
        Registers Authorization connection and components
        """

        if not self._authentication_registered:
            self._logger.error(
                "Authentication components need to be registered. Skipping.",
            )
            return self

        if self._authorization_registered:
            self._logger.warning(
                "Authorization components already registered. Skipping.",
            )
            return self

        self._logger.info(
            "Setting up and registering Authorization components...",
        )

        try:
            from castlecraft_engineer.authorization.setup import setup_authorization

            setup_authorization(self._container)
            self._authorization_registered = True
            self._logger.info(
                "Authorization components set up and registered.",
            )
        except Exception as e:
            self._logger.error(
                f"Failed to set up authorization components: {e}",
                exc_info=True,
            )

        return self

    def register(
        self,
        type_or_name: Any,
        **kwargs,
    ) -> "ContainerBuilder":
        """Directly register a component."""
        self._container.register(type_or_name, **kwargs)
        return self

    def build(self) -> punq.Container:
        """Returns the configured container."""
        self._logger.info("DI container build complete.")
        return self._container


def create_injector(container: punq.Container):
    def inject(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)

            # Identify names of arguments explicitly passed by the caller
            explicitly_passed_names = sig.bind_partial(*args, **kwargs).arguments.keys()

            kwargs_to_inject = {}
            for name, param in sig.parameters.items():
                # Attempt to inject if:
                # 1. The parameter was NOT explicitly passed by the caller.
                # 2. The parameter has a type annotation.
                if (
                    name not in explicitly_passed_names
                    and param.annotation != inspect.Parameter.empty
                ):
                    try:
                        resolved_dependency = container.resolve(
                            param.annotation,
                        )
                        kwargs_to_inject[name] = resolved_dependency
                    except punq.MissingDependencyError:
                        logger.error(
                            f"Missing dependency: {param.annotation}",
                        )
            final_kwargs = {**kwargs_to_inject, **kwargs}
            return func(*args, **final_kwargs)

        return wrapper

    return inject
