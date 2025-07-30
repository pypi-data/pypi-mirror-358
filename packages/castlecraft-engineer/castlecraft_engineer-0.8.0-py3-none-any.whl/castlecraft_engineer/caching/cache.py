import logging
from os import environ

from redis.exceptions import ConnectionError

from castlecraft_engineer.common.env import (
    DEFAULT_CACHE_REDIS_URL,
    ENV_CACHE_REDIS_MASTER_PASSWORD,
    ENV_CACHE_REDIS_MASTER_SERVICE,
    ENV_CACHE_REDIS_MASTER_USERNAME,
    ENV_CACHE_REDIS_SENTINEL_PASSWORD,
    ENV_CACHE_REDIS_SENTINEL_USERNAME,
    ENV_CACHE_REDIS_SENTINELS,
    ENV_CACHE_REDIS_URL,
    ENV_ENABLE_CACHE_REDIS_CLUSTER,
)
from castlecraft_engineer.common.redis import (
    get_async_redis_connection,
    get_redis_connection,
)

logger = logging.getLogger(__name__)


def get_redis_cache_url():
    return environ.get(ENV_CACHE_REDIS_URL, DEFAULT_CACHE_REDIS_URL)


def get_redis_cache_connection():
    try:
        return get_redis_connection(
            redis_uri=get_redis_cache_url(),
            is_sentinel_enabled=environ.get(ENV_ENABLE_CACHE_REDIS_CLUSTER),
            sentinels_uri=environ.get(ENV_CACHE_REDIS_SENTINELS),
            sentinel_username=environ.get(ENV_CACHE_REDIS_SENTINEL_USERNAME),
            sentinel_password=environ.get(ENV_CACHE_REDIS_SENTINEL_PASSWORD),
            sentinel_master_username=environ.get(
                ENV_CACHE_REDIS_MASTER_USERNAME
            ),  # noqa: E501
            sentinel_master_password=environ.get(
                ENV_CACHE_REDIS_MASTER_PASSWORD
            ),  # noqa: E501
            sentinel_master_service=environ.get(
                ENV_CACHE_REDIS_MASTER_SERVICE
            ),  # noqa: E501
        )
    except ConnectionError as exc:
        logger.error(exc)
        return None


async def get_redis_cache_async_connection():
    try:
        return await get_async_redis_connection(
            redis_uri=get_redis_cache_url(),
            is_sentinel_enabled=environ.get(ENV_ENABLE_CACHE_REDIS_CLUSTER),
            sentinels_uri=environ.get(ENV_CACHE_REDIS_SENTINELS),
            sentinel_username=environ.get(ENV_CACHE_REDIS_SENTINEL_USERNAME),
            sentinel_password=environ.get(ENV_CACHE_REDIS_SENTINEL_PASSWORD),
            sentinel_master_username=environ.get(
                ENV_CACHE_REDIS_MASTER_USERNAME
            ),  # noqa: E501
            sentinel_master_password=environ.get(
                ENV_CACHE_REDIS_MASTER_PASSWORD
            ),  # noqa: E501
            sentinel_master_service=environ.get(
                ENV_CACHE_REDIS_MASTER_SERVICE
            ),  # noqa: E501
        )
    except ConnectionError as exc:
        logger.error(exc)
        return None
