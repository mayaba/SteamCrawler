import scrapy
from ..items import GameBasicInfo


class GamesSpider(scrapy.Spider):
    name = 'games'
    allowed_domains = ['steampowered.com']
    start_urls = [
        'https://store.steampowered.com/search/?sort_by=Released_DESC&=DESC&page=1']

    def parse(self, response):
        all_games = response.xpath(
            '/html/body/div[1]/div[7]/div[4]/form/div[1]/div/div[1]/div[3]/div/div[3]/a')
        for game in all_games:
            url = game.xpath('./@href').extract_first()
            # crawl the game URL
            yield scrapy.Request(url, callback=self.parse_game)

        # TODO: parse the next page and so on until there is no next page
        page_btns = response.css('a.pagebtn')
        next_page = ''
        
        for btn in page_btns:
            btn_direction = True if btn.css('a ::text').extract_first()=='>' else False
            next_page = btn.css('a ::attr(href)').extract_first() if btn_direction else ''
        
        if next_page:
            yield scrapy.Request(next_page, callback=self.parse())

    # callback function for game url
    def parse_game(self, response):
        #convert total reviews to int
        total_reviews = int(response.css(
            'div.user_reviews_filter_menu:nth-child(1) > div:nth-child(2) > div:nth-child(1) > label:nth-child(2) > span:nth-child(1) ::text').extract_first().replace(',', '').replace('(', '').replace(')', ''))

        if total_reviews > 25:
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
            bi['early_access'] = True if response.css(
                '.early_access_header') else False

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
            yield bi
