import scrapy

class TeacherItem(scrapy.Item):
    name = scrapy.Field()   # 名言
    title = scrapy.Field()  # 作者
    info = scrapy.Field()   # 占位字段
