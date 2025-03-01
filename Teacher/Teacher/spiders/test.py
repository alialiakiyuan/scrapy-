# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy.utils.project import get_project_settings
from Teacher.items import TeacherItem  # 确保你自定义的 `TeacherItem` 存在


class TestSpider(scrapy.Spider):
    name = 'test'
    allowed_domains = ['quotes.toscrape.com']

    def __init__(self, *args, **kwargs):
        super(TestSpider, self).__init__(*args, **kwargs)
        # 获取项目配置信息
        settings = get_project_settings()
        # 连接 Redis
        self.redis_client = redis.StrictRedis(
            host=settings.get('REDIS_HOST', 'localhost'),
            port=settings.get('REDIS_PORT', 6379),
            db=settings.get('REDIS_DB', 0)
        )

    def start_requests(self):
        # 从 Redis 队列中获取初始 URL
        while True:
            url = self.redis_client.lpop('pending_urls')
            if url is None:
                break
            url = url.decode('utf-8')
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # 找到页面中所有名言块
        quotes = response.xpath("//div[@class='quote']")

        for quote in quotes:
            item = TeacherItem()

            # 提取名言和作者
            item['name'] = quote.xpath("span[@class='text']/text()").get()
            item['title'] = quote.xpath("span/small[@class='author']/text()").get()
            item['info'] = "N/A"  # 对应字段占位符

            yield item

        # 翻页逻辑，检查是否存在下一页
        next_page = response.xpath("//li[@class='next']/a/@href").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            # 将新发现的 URL 添加到 Redis 队列中
            self.redis_client.rpush('pending_urls', next_page_url)
            yield scrapy.Request(url=next_page_url, callback=self.parse)