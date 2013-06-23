from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scraper.items import FinancialOrgItem
import simplejson
import os

import sys
parentdir = os.path.dirname((os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))))
sys.path.insert(0, parentdir)
import util
import config

class FinancialOrgSpider(BaseSpider):
    name = "financial"
    allowed_domains = ["crunchbase.com"]

    clist = map(chr, range(97, 123))
    clist.append('other')
    start_urls = []
    for c in clist:
        start_urls.append( \
                "http://www.crunchbase.com/financial-organizations?c=%s" % c)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        org_urls = hxs.select( \
                '//table[@class="col2_table_listing"]//li/a/@href').extract()

        for url in org_urls:
            crunch_id = url.split("/")[-1].strip()
            api_url = "http://api.crunchbase.com/v/1/financial-organization/%s.js?api_key=%s" % \
                    (crunch_id, config.CRUNCHBASE_API_KEY)
            yield Request(api_url, callback=lambda r, 
                    crunch_id=crunch_id:self.parse_json(r, crunch_id))

    def parse_json(self, response, crunch_id):
        fpath = "scraper/crunchbase_financial_json/%s.json" % crunch_id
        with open(fpath, "w") as fh:
            fh.write(response.body)

