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
    start_urls = [
        'https://store.steampowered.com/search/?sort_by=Released_DESC&=DESC&page=1']

    def parse(self, response):
        all_games = response.xpath(
            '/html/body/div[1]/div[7]/div[4]/form/div[1]/div/div[1]/div[3]/div/div[3]/a')
        for game in all_games:
            url = game.xpath('./@href').extract_first() # extract the game URL
            yield scrapy.Request(url, callback=self.parse_game) # crawl the game URL

        # Parse the next page and so on until there is no next page
        next_page = response.xpath('//a[text() = ">"]/@href').extract_first()
        if next_page:
            yield scrapy.Request(next_page, callback=self.parse)

    # callback function for game url
    def parse_game(self, response):
        appid = response.request.url.split('/')[-3]

        if '/agecheck/app' in response.url:
            # automate choosing the date and clicking the view button
            driver = webdriver.Chrome()
            driver.get(response.url)
            ageYear = Select(driver.find_element_by_id('ageYear'))
            ageYear.select_by_value('1970')  # change the year
            view_button = driver.find_element_by_css_selector(
                '#app_agegate > div.main_content_ctn > div.agegate_text_container.btns > a:nth-child(1)')
            actionchains = ActionChains(driver)
            actionchains.click(view_button).perform()
            driver.get(response.request.url)
            driver_body = driver.page_source
            res = response.replace(body=driver_body)
            driver.quit()
        else:
            res = response

        total_reviews = res.xpath(
            '//label[@for="review_type_all"]/span/text()').extract_first()

        if total_reviews:
            reviews_int = strToInt(total_reviews)
            if reviews_int > 25:
                # create Basic Information item
                bi = GameBasicInfo()
                bi['appid'] = appid
                bi['title'] = res.css('.apphub_AppName::text').extract_first()

                # developers and publishers
                dap = response.xpath(
                    '//*[contains(@class, "dev_row")]/*[contains(@class, "summary column")]/a')
                bi['developer'] = dap[0].xpath('text()').extract()
                bi['publisher'] = dap[1].xpath('text()').extract()

                bi['early_access'] = True if res.css(
                    '.early_access_header') else False

                tags = res.xpath('//*[@class="app_tag"]/text()').extract()
                stripped_tags = []
                # strip tags from white spaces
                for tag in tags:
                    stripped_tags.append(tag.strip())

                genres = res.xpath(
                    '//div[@class="details_block"]/a[contains(@href, "genre")]/text()').extract()
                stripped_genres = []
                # strip genres from white spaces
                for genre in genres:
                    stripped_genres.append(genre.strip())

                bi['tags'] = stripped_tags
                bi['genres'] = stripped_genres
                bi['total_reviews'] = reviews_int
                bi['positive_reviews'] = strToInt(res.xpath(
                    '//label[@for="review_type_positive"]/span/text()').extract_first())
                bi['negative_reviews'] = strToInt(res.xpath(
                    '//label[@for="review_type_negative"]/span/text()').extract_first())
                bi['english_reviews'] = strToInt(res.xpath(
                    '//label[@for="review_language_mine"]/span/text()').extract_first())
                yield bi