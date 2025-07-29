import asyncio
import time
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager
from pymilvus import MilvusClient, DataType
from descartcan.config import config
from descartcan.utils.log import logger


class MilvusConnection:

    def __init__(self):
        self.uri = f"{config.MILVUS_PREFIX}://{config.MILVUS_HOST}:{config.MILVUS_PORT}"
        self.token = config.MILVUS_TOKEN
        self.db_name = config.MILVUS_DB_NAME
        self.client = None
        self.in_use = False
        self.last_used = time.time()
        self.created_at = time.time()

    def connect(self):
        if self.client is None:
            self.client = MilvusClient(
                uri=self.uri,
                token=self.token,
                db_name=self.db_name
            )
        return self.client

    def disconnect(self):
        self.client = None

    def is_connected(self):
        if self.client is None:
            return False

        try:
            self.client.list_collections()
            return True
        except Exception as e:
            logger.warning(f"连接检查失败: {e}")
            return False


class MilvusConnectionPool:
    """Milvus 连接池实现"""

    def __init__(
            self,
            max_connections: int = 10,
            min_connections: int = 2,
            max_idle_time: int = 300,  # 空闲连接的最大生存时间（秒）
            connection_timeout: int = 30,  # 获取连接的超时时间（秒）
            connection_ttl: int = 3600,  # 连接的最大生存时间（秒）
            health_check_interval: int = 60  # 健康检查间隔（秒）
    ):
        """
        初始化连接池

        Args:
            max_connections: 连接池中最大连接数
            min_connections: 连接池中最小连接数（预创建）
            max_idle_time: 空闲连接的最大生存时间（秒）
            connection_timeout: 获取连接的超时时间（秒）
            connection_ttl: 连接的最大生存时间（秒）
            health_check_interval: 健康检查间隔（秒）
        """
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.max_idle_time = max_idle_time
        self.connection_timeout = connection_timeout
        self.connection_ttl = connection_ttl
        self.health_check_interval = health_check_interval

        # 连接池
        self.pool: List[MilvusConnection] = []
        # 连接可用性信号量
        self.semaphore = asyncio.Semaphore(max_connections)
        # 连接池锁
        self.lock = asyncio.Lock()
        # 健康检查任务
        self.health_check_task = None
        # 连接池状态
        self.running = False

    async def start(self):
        """启动连接池"""
        if self.running:
            return

        self.running = True

        # 预创建连接
        async with self.lock:
            for _ in range(self.min_connections):
                conn = MilvusConnection()
                conn.connect()
                self.pool.append(conn)

        # 启动健康检查任务
        self.health_check_task = asyncio.create_task(self._health_check())

        logger.info(f"Milvus 连接池已启动，初始连接数: {self.min_connections}")

    async def stop(self):
        """停止连接池"""
        if not self.running:
            return

        self.running = False

        # 取消健康检查任务
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass

        # 关闭所有连接
        async with self.lock:
            for conn in self.pool:
                conn.disconnect()
            self.pool.clear()

        logger.info("Milvus 连接池已停止")

    async def _health_check(self):
        """定期健康检查，清理过期连接，确保最小连接数"""
        while self.running:
            try:
                await asyncio.sleep(self.health_check_interval)

                if not self.running:
                    break

                current_time = time.time()
                to_remove = []

                async with self.lock:
                    # 检查并移除过期连接
                    for conn in self.pool:
                        # 跳过正在使用的连接
                        if conn.in_use:
                            continue

                        # 检查空闲超时
                        if current_time - conn.last_used > self.max_idle_time:
                            to_remove.append(conn)
                            continue

                        # 检查连接总生存时间
                        if current_time - conn.created_at > self.connection_ttl:
                            to_remove.append(conn)
                            continue

                        # 检查连接是否有效
                        if not conn.is_connected():
                            to_remove.append(conn)

                    # 移除过期或无效连接
                    for conn in to_remove:
                        if conn in self.pool:
                            conn.disconnect()
                            self.pool.remove(conn)

                    # 确保最小连接数
                    idle_count = sum(1 for conn in self.pool if not conn.in_use)
                    for _ in range(max(0, self.min_connections - idle_count)):
                        if len(self.pool) < self.max_connections:
                            conn = MilvusConnection()
                            conn.connect()
                            self.pool.append(conn)

                logger.debug(f"健康检查完成，当前连接池大小: {len(self.pool)}, 移除: {len(to_remove)}")

            except Exception as e:
                logger.error(f"健康检查出错: {e}")

    async def get_connection(self) -> MilvusConnection:
        """获取一个可用连接"""
        if not self.running:
            await self.start()

        # 使用超时机制获取信号量
        try:
            # 创建一个任务来获取信号量，并设置超时
            acquire_task = asyncio.create_task(self.semaphore.acquire())
            done, pending = await asyncio.wait(
                [acquire_task],
                timeout=self.connection_timeout
            )

            if acquire_task not in done:
                # 取消任务
                acquire_task.cancel()
                raise TimeoutError(f"获取 Milvus 连接超时，当前连接池大小: {len(self.pool)}")
        except Exception as e:
            if not isinstance(e, TimeoutError):
                logger.error(f"获取连接信号量时出错: {e}")
            raise

        # 尝试获取空闲连接
        async with self.lock:
            # 查找空闲连接
            for conn in self.pool:
                if not conn.in_use:
                    conn.in_use = True
                    conn.last_used = time.time()
                    return conn

            # 如果没有空闲连接但未达到最大连接数，创建新连接
            if len(self.pool) < self.max_connections:
                conn = MilvusConnection()
                conn.connect()
                conn.in_use = True
                conn.last_used = time.time()
                self.pool.append(conn)
                return conn

        # 这种情况理论上不会发生，因为我们有信号量控制
        self.semaphore.release()
        raise RuntimeError("无法获取 Milvus 连接")

    def release_connection(self, conn: MilvusConnection):
        """释放连接回连接池"""
        conn.in_use = False
        conn.last_used = time.time()
        self.semaphore.release()

    @asynccontextmanager
    async def connection(self):
        """连接上下文管理器，用于自动获取和释放连接"""
        conn = await self.get_connection()
        try:
            yield conn.client
        finally:
            self.release_connection(conn)


class AsyncMilvusClient:

    _instance = None
    _pool = None

    @classmethod
    def init_milvus(cls):
        if config.MILVUS_HOST and config.MILVUS_PORT and config.MILVUS_PREFIX:
            return AsyncMilvusClient()
        return None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AsyncMilvusClient, cls).__new__(cls)
            cls._pool = MilvusConnectionPool(
                max_connections=config.MILVUS_MAX_CONNECTIONS,
                min_connections=config.MILVUS_MIN_CONNECTIONS,
                max_idle_time=config.MILVUS_MAX_IDLE_TIME,
                connection_timeout=config.MILVUS_CONNECTION_TIMEOUT,
                connection_ttl=config.MILVUS_CONNECTION_TTL,
                health_check_interval=config.MILVUS_HEALTH_CHECK_INTERVAL
            )
        return cls._instance

    async def start(self):
        await self._pool.start()

    async def stop(self):
        await self._pool.stop()

    @asynccontextmanager
    async def connection(self):
        async with self._pool.connection() as client:
            yield client

    async def create_collection(
            self,
            collection_name: str,
            dimension: int,
            description: str = "",
            metric_type: str = "COSINE"
    ):
        """
        异步创建集合

        Args:
            collection_name: 集合名称
            dimension: 向量维度
            description: 集合描述
            metric_type: 距离度量类型，如 "COSINE", "L2", "IP"
        """
        # 定义集合架构
        schema = {
            "fields": [
                {
                    "name": "id",
                    "dtype": DataType.INT64,
                    "description": "主键ID",
                    "is_primary": True,
                },
                {
                    "name": "vector",
                    "dtype": DataType.FLOAT_VECTOR,
                    "description": "向量数据",
                    "dim": dimension,
                    "is_primary": False,
                },
                {
                    "name": "metadata",
                    "dtype": DataType.JSON,
                    "description": "元数据",
                    "is_primary": False,
                }
            ],
            "description": description
        }

        index_params = {
            "metric_type": metric_type,
            "index_type": "HNSW",
            "params": {"M": 8, "efConstruction": 64}
        }

        async with self._pool.connection() as client:
            return client.create_collection(
                collection_name=collection_name,
                schema=schema,
                index_params=index_params
            )

    async def insert(
            self,
            collection_name: str,
            ids: List[int],
            vectors: List[List[float]],
            metadata: List[Dict[str, Any]] = None):
        """
        异步插入数据到集合

        Args:
            collection_name: 集合名称
            ids: ID列表
            vectors: 向量数据列表
            metadata: 元数据列表
        """
        if metadata is None:
            metadata = [{} for _ in range(len(ids))]

        data = {
            "id": ids,
            "vector": vectors,
            "metadata": metadata
        }

        async with self._pool.connection() as client:
            return client.insert(
                collection_name=collection_name,
                data=data
            )

    async def search(
            self, collection_name: str,
            query_vectors: List[List[float]],
            limit: int = 10,
            output_fields: List[str] = None,
            expr: str = None,
            search_params: Dict = None,
            anns_field: str = None,
            timeout: Optional[float] = None
    ):
        """
        异步向量搜索

        Args:
            collection_name: 集合名称
            query_vectors: 查询向量列表
            limit: 返回结果数量
            output_fields: 返回的字段列表
            expr: 过滤表达式
            search_params: 检索方法
            anns_field:
            timeout:
        """
        if not search_params:
            search_params = {
                "metric_type": "COSINE",
                "params": {"ef": 32}
            }

        async with self._pool.connection() as client:
            return client.search(
                collection_name=collection_name,
                data=query_vectors,
                limit=limit,
                output_fields=output_fields,
                filter=expr,
                search_params=search_params,
                anns_field=anns_field,
                timeout=timeout
            )

    async def delete(self, collection_name: str, ids: List[int]):
        """
        异步删除数据

        Args:
            collection_name: 集合名称
            ids: 要删除的ID列表
        """
        expr = f"id in {ids}"

        async with self._pool.connection() as client:
            return client.delete(
                collection_name=collection_name,
                expr=expr
            )

    async def drop_collection(self, collection_name: str):
        """
        异步删除集合

        Args:
            collection_name: 集合名称
        """
        async with self._pool.connection() as client:
            return client.drop_collection(collection_name)

    async def get_collection_stats(self, collection_name: str):
        """
        异步获取集合统计信息

        Args:
            collection_name: 集合名称
        """
        async with self._pool.connection() as client:
            return client.get_collection_stats(collection_name)

    async def list_collections(self):
        """异步获取所有集合列表"""
        async with self._pool.connection() as client:
            return client.list_collections()