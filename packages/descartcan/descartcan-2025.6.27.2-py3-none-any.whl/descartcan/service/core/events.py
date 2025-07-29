# -*- coding:utf-8 -*-
"""
# Time       ：2023/12/8 18:23
# Author     ：Maxwell
# version    ：python 3.9
# Description：
"""

from typing import Callable
from fastapi import FastAPI
from descartcan.service.database.mysql import register_mysql
from descartcan.service.database.redis import get_redis_client
from descartcan.service.database.milvus import AsyncMilvusClient


def startup(app: FastAPI) -> Callable:
    async def app_start() -> None:
        await register_mysql(app)

        milvus_client = AsyncMilvusClient.init_milvus()
        if milvus_client:
            app.state.milvus_client = milvus_client

        redis_client = get_redis_client()
        if redis_client:
            app.state.redis_client = await redis_client
    return app_start


def stopping(app: FastAPI) -> Callable:
    async def stop_app() -> None:
        if app.state.redis_client:
            await app.state.redis_client.close()
    return stop_app
