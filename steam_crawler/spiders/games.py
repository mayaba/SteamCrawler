import scrapy


class GamesSpider(scrapy.Spider):
    name = 'games'
    allowed_domains = ['steampowered.com']
    start_urls = [
        'http://store.steampowered.com/search/?sort_by=Released_DESC/']

    def parse(self, response):

            # if '/agecheck/app' in response.url:
            #     self.fakeAge(response.url)

        all_games = response.xpath(
            '/html/body/div[1]/div[7]/div[4]/form/div[1]/div/div[1]/div[3]/div/div[3]/a')

        for game in all_games:
            url = game.xpath('./@href').extract_first()
            # crawl the game URL
            yield scrapy.Request(url, callback=self.parse_game)


    # callback function for game url
    def parse_game(self, response):
        title = response.xpath(
            '/html/body/div[1]/div[7]/div[4]/div[1]/div[3]/div[2]/div[2]/div/div[3]/text()').extract_first()
        developer = response.xpath(
            '/html/body/div[1]/div[7]/div[4]/div[1]/div[3]/div[4]/div[1]/div/div[1]/div/div[3]/div/div[4]/div[2]/a/text()').extract()
        publisher = response.xpath(
            '/html/body/div[1]/div[7]/div[4]/div[1]/div[3]/div[4]/div[1]/div/div[1]/div/div[3]/div/div[4]/div[2]/a/text()').extract()
        url = response.request.url
        tags = response.xpath('/html/body/div[1]/div[7]/div[4]/div[1]/div[3]/div[4]/div[1]/div/div[1]/div/div[4]/div/div[2]/a/text()').extract()
        genres = response.css('div.details_block:nth-child(1) > a ::text').extract()
        stripped_tags = []
        stripped_genres = []
        

        for tag in tags:
            stripped_tags.append(tag.strip())
        
        for genre in genres:
            stripped_genres.append(genre.strip())

        
        yield {
            # TODO: add appid
            'title': title,
            'developer': developer,
            'publisher': publisher,
            'tags' : stripped_tags,
            'genres' : stripped_genres,
            'url': url,
            'headers': headers,
        }
    
    # to pypass age checker
    # def fakeAge(url):
    #     form = url.css('.agegate_birthday_selector')
    #     redirect_url = '/agecheckset/app/9200/'
