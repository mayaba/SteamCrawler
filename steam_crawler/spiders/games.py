import scrapy
from ..items import GameBasicInfo


class GamesSpider(scrapy.Spider):
    name = 'games'
    allowed_domains = ['steampowered.com']
    start_urls = [
        'https://store.steampowered.com/search/?sort_by=Released_DESC&=DESC&page=1000']

    def parse(self, response):
        all_games = response.xpath(
            '/html/body/div[1]/div[7]/div[4]/form/div[1]/div/div[1]/div[3]/div/div[3]/a')
        for game in all_games:
            url = game.xpath('./@href').extract_first()
            # crawl the game URL
            yield scrapy.Request(url, callback=self.parse_game)

        # TODO: parse the next page and so on until there is no next page
        # Example:
        # next_page = path to the URL
        # yield scrapy.Request(next_page, callback=self.parse())

    # callback function for game url
    def parse_game(self, response):
        # create Basic Information item
        bi = GameBasicInfo()

        bi['appid'] = response.request.url.split('/')[-3]
        bi['title'] = response.xpath(
            '/html/body/div[1]/div[7]/div[4]/div[1]/div[3]/div[2]/div[2]/div/div[3]/text()').extract_first()
        bi['developer'] = response.xpath(
            '/html/body/div[1]/div[7]/div[4]/div[1]/div[3]/div[4]/div[1]/div/div[1]/div/div[3]/div/div[4]/div[2]/a/text()').extract()
        bi['publisher'] = response.xpath(
            '/html/body/div[1]/div[7]/div[4]/div[1]/div[3]/div[4]/div[1]/div/div[1]/div/div[3]/div/div[4]/div[2]/a/text()').extract()
        tags = response.xpath(
            '/html/body/div[1]/div[7]/div[4]/div[1]/div[3]/div[4]/div[1]/div/div[1]/div/div[4]/div/div[2]/a/text()').extract()
        genres = response.css(
            'div.details_block:nth-child(1) > a ::text').extract()

        # total_reviews = response.css(
        #     'div.user_reviews_filter_menu:nth-child(1) > div:nth-child(2) > div:nth-child(1) > label:nth-child(2) > span:nth-child(1) ::text').extract_first()
        # positive_reviews = response.css(
        #     'div.user_reviews_filter_menu:nth-child(1) > div:nth-child(2) > div:nth-child(1) > label:nth-child(5) > span:nth-child(1) ::text').extract_first()
        # negative_reviews = response.css(
        #     'div.user_reviews_filter_menu:nth-child(1) > div:nth-child(2) > div:nth-child(1) > label:nth-child(8) > span:nth-child(1) ::text').extract_first()
        # english_reviews = response.css(
        #     'div.user_reviews_filter_menu:nth-child(3) > div:nth-child(2) > div:nth-child(1) > label:nth-child(5) > span:nth-child(1) ::text').extract_first()

        early_access = response.css('.early_access_header')
        if early_access:
            is_early_access = True
        else:
            is_early_access = False

        stripped_tags = []
        # strip tags from white spaces
        for tag in tags:
            stripped_tags.append(tag.strip())

        stripped_genres = []
        # strip genres from white spaces
        for genre in genres:
            stripped_genres.append(genre.strip())

        bi['tags'] = stripped_tags
        bi['genres'] = stripped_genres
        bi['early_access'] = is_early_access

        # yield {
        #     'appid': appid,
        #     'title': title,
        #     'developer': developer,
        #     'publisher': publisher,
        #     'tags': stripped_tags,
        #     'genres': stripped_genres,
        #     'url': url,
        #     'early_access': is_early_access,
        #     'total_reviews': total_reviews,
        #     'positive_reviews': positive_reviews,
        #     'negative_reviews': negative_reviews,
        #     'english_reviews': english_reviews,
        # }

        yield bi
# links to next pages
# https://store.steampowered.com/search/?sort_by=Released_DESC&sort_order=DESC&page=2
# a.pagebtn <- extract all pagebtn and take the second one
