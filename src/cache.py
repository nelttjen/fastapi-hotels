import hashlib
import logging
from typing import Any, Optional, Callable

from redis import asyncio as aioredis
from fastapi import Request, Response
from fastapi_cache import FastAPICache

from src.config import redis_settings

logger = logging.getLogger('debugger')
redis = aioredis.from_url(redis_settings.REDIS_URL, encoding='utf8', decode_responses=True)


class KeyBuilderCache:

    @staticmethod
    def key_builder(
            func: Callable,
            namespace: Optional[str] = '',
            request: Request = None,
            response: Response = None,
            *args: Any, **kwargs,
    ) -> str:
        """
        Build a cache key for the given function.

        :param func: The function to build a cache key for.
        :param namespace: The namespace to use for the cache key.
        :param request: The current request.
        :param response: The current response.
        :param args: The positional arguments to pass to the function.
        :param kwargs: The keyword arguments to pass to the function.
        :return: The cache key.
        """
        prefix = FastAPICache.get_prefix()

        key = f'{prefix}:{namespace}:{func.__module__}:{func.__name__}'

        if args_str := (str(args) + str(kwargs)):
            args_hash = hashlib.sha256(args_str.encode('utf-8')).hexdigest()
            key += f':{args_hash}'

        request_str = ''

        if request:
            request_str += f':{request.method}:{request.url}'
        if response:
            request_str += f':{response.status_code}'
        if request_str:
            request_hash = hashlib.sha256(request_str.encode('utf-8')).hexdigest()
            key += f':{request_hash}'

        logger.debug(f'key_builder: {key}')
        return key

    @staticmethod
    async def clear_cache_for_func(
            func: Callable,
    ):
        """
        Clear the cache for the given function.

        :param func: The function to clear the cache for.
        """
        prefix = FastAPICache.get_prefix()
        pattern = f'{prefix}:clearable-{func.__name__}:*'
        logger.debug(f'clear_cache_for_func: {pattern}')
        keys = await redis.keys(pattern)
        result = 0
        if keys:
            result = await redis.delete(*keys)
        logger.debug(f'cleared caches: {result}')