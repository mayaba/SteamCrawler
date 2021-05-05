import scrapy
from ..items import ReleaseNotes
from w3lib.url import url_query_parameter
from scrapy.http import FormRequest, Request
import datetime
import re


def strToFloat(x):
    x = x.replace(',', '')
    try:
        return float(x)
    except:
        return x


def strToInt(x):
    try:
        return int(strToFloat(x))
    except:
        return x


def getPage(response):
    from_page = response.meta.get('from_page', None)

    if from_page:
        page = from_page + 1
    else:
        page = url_query_parameter(response.url, 'p', None)
        if page:
            page = strToInt(page)

    return page


def getProductId(response):
    product_id = response.meta.get('product_id', None)

    if not product_id:
        try:
            return re.findall("app/(.+?)/", response.url)[0]
        except:
            return None
    else:
        return product_id


# check if the title includes one of news_include_list
def doesContain(title):
    try:
        news_include_list = ['update', 'release', 'patch', 'hotfix',
                             'change log', 'version', 'release notes']
        does_contain = any(ele in title for ele in news_include_list)
        return does_contain
    except:
        print('Error' + title)


class NewsSpider(scrapy.Spider):
    name = 'news'
    allowed_domains = ['steamcommunity.com']

    def __init__(self, news_urls=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.news_urls = news_urls

    def read_urls(self):
        with open(self.news_urls, 'r') as f:
            for url in f:
                url = url.strip()
                if url:
                    yield scrapy.Request(url, callback=self.parse)

    def start_requests(self):
        if self.news_urls:
            yield from self.read_urls()

    def parse(self, response):
        page = getPage(response)
        product_id = getProductId(response)

        # get all releae notes
        # all_news = response.css(".apphub_CardContentMain")
        all_news = response.xpath(
            '//div[@class="apphub_CardContentMain"]/parent::div')

        if all_news:
            for n in all_news:
                title = n.css(
                    '.apphub_CardContentNewsTitle::text').extract_first()
                
                is_update = doesContain(title.lower())
                if (is_update):
                    # TODO: get the content
                    rn = ReleaseNotes()
                    rn['appid'] = product_id
                    rn['title'] = title
                    rn['notes_body'] = ''.join(
                        n.css('.apphub_CardTextContent ::text').extract()).strip()
                    rn['rate'] = int(
                        n.css('.apphub_CardRating::text').extract_first().replace(',', ''))
                    rn['comment_count'] = int(
                        n.css('.apphub_CardCommentCount::text').extract_first().replace(',', ''))
                    yield rn
                # else:
                #     print('------------------------------------------')
                #     print('Error in response ' + response.request.url)
                #     print(n.css(
                #         '.apphub_CardContentNewsTitle::text').extract_first())
                #     print(all_news.index(n))
                #     print('------------------------------------------')

        # Navigate to next page.
        form = response.xpath('//form[contains(@id, "MoreContentForm")]')
        if form:
            yield self.goNextPage(form, page, product_id)

    def goNextPage(self, form, page=None, product_id=None):
        names = form.xpath('input/@name').extract()
        values = form.xpath('input/@value').extract()

        return FormRequest(
            url=form.xpath('@action').extract_first(),
            method='GET',
            formdata=dict(zip(names, values)),
            callback=self.parse,
            meta=dict(prev_page=page, product_id=product_id)
        )
