import logging
from scrapy.utils.project import get_project_settings
import redis

# 配置日志记录
logging.basicConfig(level=logging.INFO)

# 获取 Scrapy 项目的配置信息
settings = get_project_settings()

# 连接 Redis
redis_client = redis.StrictRedis(
    host=settings.get('REDIS_HOST', 'localhost'),
    port=settings.get('REDIS_PORT', 6379),
    db=settings.get('REDIS_DB', 0)
)

# 输出 Redis 连接信息
logging.info(f"Redis 连接信息: host={redis_client.connection_pool.connection_kwargs['host']}, port={redis_client.connection_pool.connection_kwargs['port']}, db={redis_client.connection_pool.connection_kwargs['db']}")

# 测试 Redis 连接
try:
    # 设置一个测试键值对
    redis_client.set('test_key', 'test_value')
    # 获取键的值
    value = redis_client.get('test_key')
    logging.info(f"Redis 连接成功，获取的值: {value.decode('utf-8')}")
except Exception as e:
    logging.error(f"Redis 连接失败: {e}")