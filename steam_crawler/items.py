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
    total_reviews = scrapy.Field()
    positive_reviews = scrapy.Field()
    negative_reviews = scrapy.Field()
    english_reviews = scrapy.Field()

# reviews from community hub
class GameReview(scrapy.Item):
    # TODO: add appid, positive and negative reviews, and date duration (since today)
    # appid = scrapy.Field()
    rank = scrapy.Field()
    date = scrapy.Field()
    hours = scrapy.Field()
    review_text = scrapy.Field()
    positive_review = scrapy.Field()
    date_duration_days = scrapy.Field()
