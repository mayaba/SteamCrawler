import scrapy
from ..items import GameReview


class ReviewsSpider(scrapy.Spider):
    name = 'reviews'
    allowed_domains = ['steamcommunity.com']
    start_urls = [
        'http://steamcommunity.com/app/316790/reviews/?browsefilter=mostrecent&p=1&filterLanguage=english']

    def parse(self, response):
        # get all reviews
        all_reviews = response.css("div .apphub_Card")

        # add enumeration if you need the order of the review
        for r in all_reviews:
            ur = GameReview()
            # get review data
            ur['rate'] = r.css(".title::text").extract_first()
            ur['date'] = r.css(".date_posted::text").extract_first().split(
                ':')[-1].strip()
            ur['hours'] = float(r.css(
                ".hours::text").extract_first().split(' ')[0].strip())
            ur['text'] = ''.join(
                r.css(".apphub_CardTextContent::text").extract()).strip()

            yield ur
