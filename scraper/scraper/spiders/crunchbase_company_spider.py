from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scraper.items import CompanyItem

from datetime import datetime
import os

import sys
parentdir = os.path.dirname((os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))))
sys.path.insert(0, parentdir)
import util
import config

class CompanySpider(BaseSpider):
    name = "company"
    allowed_domains = ["crunchbase.com"]

    clist = map(chr, range(97, 123))
    clist.append('other')
    start_urls = []
    for c in clist:
        start_urls.append("http://www.crunchbase.com/companies?c=%s" % c)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        company_urls = hxs.select('//table[@class="col2_table_listing"]//li/a/@href').extract()

        for url in company_urls:
            crunch_id = url.split("/")[-1].strip()
            api_url = "http://api.crunchbase.com/v/1/company/%s.js?api_key=%s" % \
                    (crunch_id, config.CRUNCHBASE_API_KEY)
            yield Request(api_url, callback=lambda r, crunch_id=crunch_id:self.parse_json(r, crunch_id))

    def parse_json(self, response, crunch_id):
        fpath = "scraper/crunchbase_company_json/%s.json" % crunch_id
        with open(fpath, "w") as fh:
            fh.write(response.body)

    """
    Deprecated
    """
    def parse_company(self, response):
        hxs = HtmlXPathSelector(response)
        
        # No valid information about the company, just skip
        if len(hxs.select('//div[@id="col1"]/div[@class="col1_content"]/table')) == 0:
            return

        index = -1
        h2s = hxs.select('//div[@id="col1"]/h2')
        for ind, h2 in enumerate(h2s):
            if h2.select("text()").extract()[0].strip() == "General Information":
                index = ind
                break

        item = CompanyItem()
        item['name'] = hxs.select('//div[@id="col2_internal"]/h1/text()').extract()[0].strip()
        item['crunch_id'] = response.url.split('/')[-1]

        if len(hxs.select('//span[@id="num_employees"]/text()').extract()) > 0:
            item['employee_num'] = hxs.select('//span[@id="num_employees"]/text()').extract()[0]

        trs = hxs.select('//div[@id="col1"]/div[@class="col1_content"][%d]/table//tr' % (index+1))
        for tr in trs:
            title = tr.select('td[@class="td_left"]/text()').extract()[0].strip()
            if len(tr.select('td[@class="td_right"]/a')) > 0:
                value = tr.select('td[@class="td_right"]/a/text()').extract()[0].strip()
            else:
                if len(tr.select('td[@class="td_right"]/text()').extract()) > 0:
                    value = tr.select('td[@class="td_right"]/text()').extract()[0].strip()
                else:
                    value = None

            if title == "Website":
                item['website'] = value
            elif title == "Blog":
                item['blog'] = value
            elif title == "Category":
                item['category'] = value
            elif title == "Twitter":
                item['twitter'] = value
            elif title == "Email":
                item['email'] = value
            elif title == "Founded":
                if "/" in value:
                    year = value.split('/')[-1]
                    if int(year) > datetime.today().year:
                        value = "19" + value
                    else:
                        value = "20" + value
                else:
                    item['founded'] = value

        return item
