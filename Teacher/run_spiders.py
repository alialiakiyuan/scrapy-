import sys
import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from Teacher.spiders.test import TestSpider  # 根据实际项目结构修改
from hdfs import InsecureClient
from scrapy.utils.project import get_project_settings

def run_spiders_with_strategies():
    settings = Settings()
    settings.setmodule('scrapy.settings.default_settings')
    process = CrawlerProcess(settings)

    # 获取 Scrapy 项目的配置信息
    scrapy_settings = get_project_settings()

    # 连接 HDFS
    hdfs_client = InsecureClient(f"http://{scrapy_settings.get('HDFS_HOST', 'localhost')}:{scrapy_settings.get('HDFS_PORT', 9870)}", user='hdfs')

    # 从 HDFS 读取待爬取的 URL
    hdfs_file_path = '/user/hdfs/pending_urls.txt'
    with hdfs_client.read(hdfs_file_path) as reader:
        urls = [line.decode('utf-8').strip() for line in reader]

    for url in urls:
        process.crawl(TestSpider, start_urls=[url])

    # 启动爬虫进程
    process.start()

if __name__ == "__main__":
    run_spiders_with_strategies()