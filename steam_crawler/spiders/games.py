import scrapy
from ..items import GameBasicInfo

# to automate the bypassing of agecheker pages
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select


def strToInt(s):
    return int(s.replace(',', '').replace('(', '').replace(')', ''))


class GamesSpider(scrapy.Spider):
    name = 'games'
    allowed_domains = ['steampowered.com']
    # start_urls = [
    #     'https://store.steampowered.com/search/?sort_by=Released_DESC&=DESC&page=1000']
    start_urls = ['http://store.steampowered.com/app/9200/']

    def parse(self, response):
        # if '/agecheck/app' in response.url:
        driver = webdriver.Chrome()
        driver.get(response.url)
        ageYear = Select(driver.find_element_by_id('ageYear'))
        ageYear.select_by_value('1970')
        view_button = driver.find_element_by_css_selector(
            '#app_agegate > div.main_content_ctn > div.agegate_text_container.btns > a:nth-child(1)')
        actionchains = ActionChains(driver)
        actionchains.click(view_button).perform()
        driver.get('https://store.steampowered.com/app/9200/')
        driver_body = driver.page_source
        res = response.replace(body=driver_body)
        driver.quit()

        total_reviews = res.css(
            'div.user_reviews_filter_menu:nth-child(1) > div:nth-child(2) > div:nth-child(1) > label:nth-child(2) > span:nth-child(1) ::text').extract_first()

        if total_reviews:
            reviews_int = strToInt(total_reviews)
            if reviews_int > 25:
                # create Basic Information item
                bi = GameBasicInfo()
                bi['appid'] = res.url.split('/')[-3]
                bi['title'] = res.xpath(
                    '/html/body/div[1]/div[7]/div[4]/div[1]/div[3]/div[2]/div[2]/div/div[3]/text()').extract_first()
                bi['developer'] = res.xpath(
                    '/html/body/div[1]/div[7]/div[4]/div[1]/div[3]/div[4]/div[1]/div/div[1]/div/div[3]/div/div[4]/div[2]/a/text()').extract()
                bi['publisher'] = res.xpath(
                    '//*[@id="game_highlights"]/div[1]/div/div[3]/div/div[5]/div[2]/a/text()').extract()
                tags = res.xpath(
                    '/html/body/div[1]/div[7]/div[4]/div[1]/div[3]/div[4]/div[1]/div/div[1]/div/div[4]/div/div[2]/a/text()').extract()
                genres = res.css(
                    'div.details_block:nth-child(1) > a ::text').extract()
                bi['early_access'] = True if res.css(
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
                bi['total_reviews'] = reviews_int
                bi['positive_reviews'] = strToInt(res.css(
                    'div.user_reviews_filter_menu:nth-child(1) > div:nth-child(2) > div:nth-child(1) > label:nth-child(5) > span:nth-child(1) ::text').extract_first())
                bi['negative_reviews'] = strToInt(res.css(
                    'div.user_reviews_filter_menu:nth-child(1) > div:nth-child(2) > div:nth-child(1) > label:nth-child(8) > span:nth-child(1) ::text').extract_first())
                bi['english_reviews'] = strToInt(res.css(
                    'div.user_reviews_filter_menu:nth-child(3) > div:nth-child(2) > div:nth-child(1) > label:nth-child(5) > span:nth-child(1) ::text').extract_first())
                yield bi

        # all_games = response.xpath(
        #     '/html/body/div[1]/div[7]/div[4]/form/div[1]/div/div[1]/div[3]/div/div[3]/a')
        # for game in all_games:
        #     url = game.xpath('./@href').extract_first()
        #     # crawl the game URL
        #     yield scrapy.Request(url, callback=self.parse_game)

        # TODO: parse the next page and so on until there is no next page
        # page_btns = response.css('a.pagebtn')
        # next_page = ''

        # for btn in page_btns:
        #     btn_direction = True if btn.css(
        #         'a ::text').extract_first() == '>' else False
        #     next_page = btn.css(
        #         'a ::attr(href)').extract_first() if btn_direction else ''

        # if next_page:
        #     yield scrapy.Request(next_page, callback=self.parse)

    # callback function for game url
    # def parse_game(self, response):
        # # if '/agecheck/app' in response.url:
        # driver = webdriver.Chrome()
        # driver.get(response.url)
        # ageYear = Select(driver.find_element_by_id('ageYear'))
        # ageYear.select_by_value('1970')
        # view_button = driver.find_element_by_css_selector(
        #     '#app_agegate > div.main_content_ctn > div.agegate_text_container.btns > a:nth-child(1)')
        # actionchains = ActionChains(driver)
        # actionchains.click(view_button).perform()
        # driver.get('https://store.steampowered.com/app/9200/')
        # driver_body = driver.page_source
        # resopnse = response.replace(body=driver_body)
        # driver.quit()

        # total_reviews = response.css(
        #     'div.user_reviews_filter_menu:nth-child(1) > div:nth-child(2) > div:nth-child(1) > label:nth-child(2) > span:nth-child(1) ::text').extract_first()

        # if total_reviews:
        #     reviews_int = strToInt(total_reviews)
        #     if reviews_int > 25:
        #         # create Basic Information item
        #         bi = GameBasicInfo()
        #         bi['appid'] = response.request.url.split('/')[-3]
        #         bi['title'] = response.xpath(
        #             '/html/body/div[1]/div[7]/div[4]/div[1]/div[3]/div[2]/div[2]/div/div[3]/text()').extract_first()
        #         bi['developer'] = response.xpath(
        #             '/html/body/div[1]/div[7]/div[4]/div[1]/div[3]/div[4]/div[1]/div/div[1]/div/div[3]/div/div[4]/div[2]/a/text()').extract()
        #         bi['publisher'] = response.xpath(
        #             '/html/body/div[1]/div[7]/div[4]/div[1]/div[3]/div[4]/div[1]/div/div[1]/div/div[3]/div/div[4]/div[2]/a/text()').extract()
        #         tags = response.xpath(
        #             '/html/body/div[1]/div[7]/div[4]/div[1]/div[3]/div[4]/div[1]/div/div[1]/div/div[4]/div/div[2]/a/text()').extract()
        #         genres = response.css(
        #             'div.details_block:nth-child(1) > a ::text').extract()
        #         bi['early_access'] = True if response.css(
        #             '.early_access_header') else False

        #         stripped_tags = []
        #         # strip tags from white spaces
        #         for tag in tags:
        #             stripped_tags.append(tag.strip())

        #         stripped_genres = []
        #         # strip genres from white spaces
        #         for genre in genres:
        #             stripped_genres.append(genre.strip())

        #         bi['tags'] = stripped_tags
        #         bi['genres'] = stripped_genres
        #         bi['total_reviews'] = reviews_int
        #         bi['positive_reviews'] = strToInt(response.css(
        #             'div.user_reviews_filter_menu:nth-child(1) > div:nth-child(2) > div:nth-child(1) > label:nth-child(5) > span:nth-child(1) ::text').extract_first())
        #         bi['negative_reviews'] = strToInt(response.css(
        #             'div.user_reviews_filter_menu:nth-child(1) > div:nth-child(2) > div:nth-child(1) > label:nth-child(8) > span:nth-child(1) ::text').extract_first())
        #         bi['english_reviews'] = strToInt(response.css(
        #             'div.user_reviews_filter_menu:nth-child(3) > div:nth-child(2) > div:nth-child(1) > label:nth-child(5) > span:nth-child(1) ::text').extract_first())
        #         yield bi
