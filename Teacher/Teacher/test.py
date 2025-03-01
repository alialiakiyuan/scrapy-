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
        # 订阅任务状态更新频道
        self.pubsub = self.redis_client.pubsub()
        self.pubsub.subscribe('task_status_update')

    def start_requests(self):
        # 从 Redis 队列中获取初始 URL
        while True:
            url = self.redis_client.lpop('pending_urls')
            if url is None:
                break
            url = url.decode('utf-8')
            # 标记任务开始
            self.redis_client.set(f"task_status_{url}", "started")
            # 发布任务开始消息
            self.redis_client.publish('task_status_update', f"{url} started")
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # 检查网页中的 meta 标签
        meta_robots = response.xpath('//meta[@name="robots"]/@content').get()
        if meta_robots and ('noindex' in meta_robots or 'nofollow' in meta_robots):
            # 如果存在禁抓标记，不处理该页面
            self.logger.info(f"页面 {response.url} 存在禁抓标记，跳过该页面")
            return

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

        # 标记任务完成
        self.redis_client.set(f"task_status_{response.url}", "completed")
        # 发布任务完成消息
        self.redis_client.publish('task_status_update', f"{response.url} completed")

    def closed(self, reason):
        # 爬虫关闭时的处理逻辑
        print(f"爬虫 {self.name} 关闭，原因: {reason}")
        # 取消订阅
        self.pubsub.unsubscribe('task_status_update')