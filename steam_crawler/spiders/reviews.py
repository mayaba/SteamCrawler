import scrapy
from ..items import GameReview
from w3lib.url import url_query_parameter
from scrapy.http import FormRequest, Request
import re



# to remove emojis from reviews
def removeEmoji(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)


def str_to_float(x):
    x = x.replace(',', '')
    try:
        return float(x)
    except:
        return x


def str_to_int(x):
    try:
        return int(str_to_float(x))
    except:
        return x



def get_page(response):
    from_page = response.meta.get('from_page', None)

    if from_page:
        page = from_page + 1
    else:
        page = url_query_parameter(response.url, 'p', None)
        if page:
            page = str_to_int(page)

    return page


def get_product_id(response):
    product_id = response.meta.get('product_id', None)

    if not product_id:
        try:
            return re.findall("app/(.+?)/", response.url)[0]
        except:
            return None
    else:
        return product_id


class ReviewsSpider(scrapy.Spider):
    name = 'reviews'
    allowed_domains = ['steamcommunity.com']
    start_urls = [
        'http://steamcommunity.com/app/316790/reviews/?browsefilter=mostrecent&p=1&filterLanguage=english']

    def parse(self, response):

        page = get_page(response)
        product_id = get_product_id(response)

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

        # Navigate to next page.
        form = response.xpath('//form[contains(@id, "MoreContentForm")]')
        if form:
            yield self.process_pagination_form(form, page, product_id)

    def process_pagination_form(self, form, page=None, product_id=None):
        action = form.xpath('@action').extract_first()
        names = form.xpath('input/@name').extract()
        values = form.xpath('input/@value').extract()

        formdata = dict(zip(names, values))
        meta = dict(prev_page=page, product_id=product_id)

        return FormRequest(
        url=action,
        method='GET',
        formdata=formdata,
        callback=self.parse,
        meta=meta
        )


# TODO: Read about meta in scrapy
# //*[@id="AppHubCards"]/div[contains(@id, "page")]
