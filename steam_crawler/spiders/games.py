import scrapy
from ..items import GameBasicInfo
# to automate the bypassing of agecheker pages
from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select


def strToInt(s):
    try:
        return int(s.replace(',', '').replace('(', '').replace(')', ''))
    except:
        print('Error')


class GamesSpider(scrapy.Spider):
    name = 'games'
    handle_httpstatus_list = [500]
    allowed_domains = ['steampowered.com']
    start_urls = [
        'https://store.steampowered.com/search/?sort_by=Released_DESC&=DESC&page=1420']

    def __init__(self):
        self.failed_urls = open("failed_urls.txt", "w")

    def parse(self, response):
        valid_next_page = response.xpath('//p[contains(text(), "No results")]/text()').extract_first()

        if not valid_next_page:
            if response.status == 500:
                print('==========================================================')
                print('[-] 500 Error in url' + response.url)
                print('==========================================================')
                self.failed_urls.write(response.url)
                # yield a request to the next page
                next_page_num = int(response.url.split('=')[-1]) + 1
                next_page_req = 'https://store.steampowered.com/search/?sort_by=Released_DESC&sort_order=DESC&page=' + str(next_page_num)
                yield scrapy.Request(next_page_req, callback=self.parse)
            else:
                try:
                    all_games = response.xpath(
                        '/html/body/div[1]/div[7]/div[4]/form/div[1]/div/div[1]/div[3]/div/div[3]/a')
                    for game in all_games:
                        # extract the game URL
                        url = game.xpath('./@href').extract_first()
                        # crawl the game URL
                        yield scrapy.Request(url, callback=self.parse_game)

                    print('==========================================================')
                    print('just finished' + response.request.url)
                    print('just finished' + response.request.url)
                    print('just finished' + response.request.url)
                    print('==========================================================')
                    # Parse the next page and so on until there is no next page
                    next_page = response.xpath(
                        '//a[text() = ">"]/@href').extract_first()
                    if next_page:
                        yield scrapy.Request(next_page, callback=self.parse)
                    else:
                        self.failed_urls.close()
                        print('===========================================')
                        print('[+] Done crawling')
                        print('===========================================')
                except:
                    print('Error')
    
        else:
            print('===========================================')
            print('[+] Done crawling')
            print('===========================================')

    # callback function for game url
    def parse_game(self, response):
        try:
            appid = response.request.url.split('/')[-3]
            mature_content = ''

            if '/agecheck/app' in response.url:
                # make the browser headless
                # chrome_options = Options()
                # chrome_options.add_argument("--headless")
                # driver = webdriver.Chrome(options=chrome_options)
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
                mature_content = True
            else:
                mature_content = False
                res = response

            total_reviews = res.xpath(
                '//label[@for="review_type_all"]/span/text()').extract_first()

            if total_reviews:
                reviews_int = strToInt(total_reviews)
                if reviews_int > 25:
                    # create Basic Information item
                    bi = GameBasicInfo()
                    bi['appid'] = appid
                    bi['title'] = res.css(
                        '.apphub_AppName::text').extract_first()

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
                    bi['mature_content'] = mature_content
                    yield bi
        except:
            print('Error')
