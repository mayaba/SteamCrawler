import scrapy
from ..items import GameReview
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


def convertToDate(full_date):
    if ',' in full_date:
        date = full_date.split(' ')
        day = int(date[1].strip(','))
        month = datetime.datetime.strptime(date[0], "%B").month
        year = int(date[2])
    else:
        date = full_date.split(' ')
        day = int(date[1]) if date[0].isalpha() else int(date[0])
        month_name = date[0] if date[0].isalpha() else date[1]
        month = datetime.datetime.strptime(month_name, "%B").month
        year = datetime.datetime.now().year

    return datetime.date(year, month, day)

# remove emojis from review text


def removeEmojis(text):
    regrex_pattern = re.compile(pattern="["
                                u"\U0001F600-\U0001F64F"  # emoticons
                                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                "]+", flags=re.UNICODE)
    return regrex_pattern.sub(r'', text)


def readFile(inputFile):
    file = open(inputFile, "r")
    lines = file.readlines()
    file.close
    strtipedLines = []
    for line in lines:
        strtipedLines.append(line.strip('\n'))
    return strtipedLines


class ReviewsSpider(scrapy.Spider):
    name = 'reviews'
    allowed_domains = ['steamcommunity.com']

    def __init__(self, url_file=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_file = url_file

    def read_urls(self):
        with open(self.url_file, 'r') as f:
            for url in f:
                url = url.strip()
                if url:
                    yield scrapy.Request(url, callback=self.parse)

    def start_requests(self):
        if self.url_file:
            yield from self.read_urls()

    def parse(self, response):
        page = getPage(response)
        product_id = getProductId(response)

        # get all reviews
        all_reviews = response.css("div .apphub_Card")

        # add enumeration if you need the order of the review
        for r in all_reviews:
            # check if the review is empty
            review_text = removeEmojis(
                ''.join(r.css(".apphub_CardTextContent::text").extract()).strip())
            if review_text:
                ur = GameReview()
                # get review data
                ur['appid'] = response.request.url
                rank = r.css(".title::text").extract_first()
                ur['rank'] = rank
                review_date = convertToDate(
                    r.css(".date_posted::text").extract_first().split(':')[-1].strip())
                ur['date'] = review_date
                ur['hours'] = float(r.css(
                    ".hours::text").extract_first().split(' ')[0].strip())
                ur['review_text'] = review_text
                ur['positive_review'] = True if rank == 'Recommended' else False
                duration = str(datetime.date.today() -
                               review_date).split(',')[0].split(' ')[0]
                ur['date_duration_days'] = duration
                yield ur

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
