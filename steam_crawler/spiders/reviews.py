import scrapy
from ..items import GameReview


class ReviewsSpider(scrapy.Spider):
    name = 'reviews'
    allowed_domains = ['steamcommunity.com']
    start_urls = ['http://steamcommunity.com/']
    appids = '1189690'

    def parse(self, response):
        pass


    def getReviews(self, response):
        pass
