import redis
from scrapy.utils.project import get_project_settings

# 获取 Scrapy 项目的配置信息
settings = get_project_settings()

# 连接 Redis
redis_client = redis.StrictRedis(
    host=settings.get('REDIS_HOST', 'localhost'),
    port=settings.get('REDIS_PORT', 6379),
    db=settings.get('REDIS_DB', 0)
)

# 代理 IP 列表
proxy_list = [
    'http://1.1.1.1:8080',
    'http://2.2.2.2:8080',
    'http://3.3.3.3:8080'
]

# 将代理 IP 列表存储到 Redis 中
for proxy in proxy_list:
    redis_client.rpush('proxy_pool', proxy)