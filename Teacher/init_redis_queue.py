# Teacher/init_redis_queue.py
from hdfs import InsecureClient
from scrapy.utils.project import get_project_settings
import redis
import os

# 获取 Scrapy 项目的配置信息
settings = get_project_settings()

# 连接 HDFS
try:
    hdfs_client = InsecureClient(f"http://{settings.get('HDFS_HOST', 'localhost')}:{settings.get('HDFS_PORT', 9870)}", user='hdfs')
    print("成功连接到 HDFS")
except Exception as e:
    print(f"连接 HDFS 失败: {e}")
    raise

# 连接 Redis
try:
    redis_client = redis.StrictRedis(
        host=settings.get('REDIS_HOST', 'localhost'),
        port=settings.get('REDIS_PORT', 6379),
        db=settings.get('REDIS_DB', 0)
    )
    print("成功连接到 Redis")
except Exception as e:
    print(f"连接 Redis 失败: {e}")
    raise

# 从文件中读取种子 URL 列表
def read_seed_urls_from_file(file_path):
    try:
        with open(file_path, 'r') as f:
            seed_urls = [line.strip() for line in f.readlines()]
        # 去除重复的 URL
        unique_urls = list(set(seed_urls))
        print(f"从文件 {file_path} 中读取到 {len(unique_urls)} 个种子 URL")
        return unique_urls
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到")
        return []

# 读取种子 URL
seed_urls = read_seed_urls_from_file('seed_urls.txt')

# 将种子 URL 写入 HDFS
if seed_urls:
    hdfs_file_path = '/user/hdfs/pending_urls.txt'
    try:
        with hdfs_client.write(hdfs_file_path, overwrite=True) as writer:
            for url in seed_urls:
                writer.write(f"{url}\n".encode('utf-8'))
        print(f"成功将 {len(seed_urls)} 个种子 URL 写入 HDFS")
    except Exception as e:
        print(f"写入 HDFS 失败: {e}")
else:
    print("没有找到有效的种子 URL")

# 从 HDFS 读取 URL 并写入 Redis
try:
    with hdfs_client.read(hdfs_file_path) as reader:
        urls = [line.decode('utf-8').strip() for line in reader]
    for url in urls:
        redis_client.rpush('pending_urls', url)
    print(f"成功将 {len(urls)} 个 URL 从 HDFS 读取并写入 Redis")
except Exception as e:
    print(f"从 HDFS 读取或写入 Redis 失败: {e}")