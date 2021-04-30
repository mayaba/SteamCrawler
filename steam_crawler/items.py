# Define here the models for your scraped items
#
# See documentation in=
# https=//docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GameBasicInfo(scrapy.Item):
    # define the fields for your item here like=
    appid = scrapy.Field()
    title = scrapy.Field()
    developer = scrapy.Field()
    publisher = scrapy.Field()
    tags = scrapy.Field()
    genres = scrapy.Field()
    early_access = scrapy.Field()
