# -*- coding: utf-8 -*-
import scrapy
from Teacher.items import TeacherItem  # 确保你自定义的 `TeacherItem` 存在


class TestSpider(scrapy.Spider):
    name = 'test1'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        # 找到页面中所有名言块
        quotes = response.xpath("//div[@class='quote']")
        print(len(quotes))

