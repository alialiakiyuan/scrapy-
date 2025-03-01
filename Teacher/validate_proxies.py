import redis
from scrapy.utils.project import get_project_settings
import requests

# 获取 Scrapy 项目的配置信息
settings = get_project_settings()

# 连接 Redis
redis_client = redis.StrictRedis(
    host=settings.get('REDIS_HOST', 'localhost'),
    port=settings.get('REDIS_PORT', 6379),
    db=settings.get('REDIS_DB', 0)
)

# 验证代理 IP 的有效性
def validate_proxy(proxy):
    try:
        response = requests.get('http://www.baidu.com', proxies={'http': proxy, 'https': proxy}, timeout=5)
        if response.status_code == 200:
            return True
        else:
            return False
    except:
        return False

# 定期验证代理 IP 列表
def validate_proxy_list():
    proxy_count = redis_client.llen('proxy_pool')
    for i in range(proxy_count):
        proxy = redis_client.lindex('proxy_pool', i).decode('utf-8')
        if not validate_proxy(proxy):
            redis_client.lrem('proxy_pool', 0, proxy)

# 调用验证函数
validate_proxy_list()