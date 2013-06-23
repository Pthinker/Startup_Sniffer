from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

import json
from datetime import datetime
import os

import sys
parentdir = os.path.dirname((os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))))
sys.path.insert(0, parentdir)
import util
import config

class AngellistSpider(BaseSpider):
    name = "angellist_people"
    allowed_domains = ["angel.co"]

    start_urls = []
    for i in xrange(300001, 400001, 50):
        cids = range(i, i+50)
        list_str = ",".join(map(str,cids))
        start_urls.append("https://api.angel.co/1/users/batch?ids=%s&access_token=%s" \
                % (list_str, config.ANGELLIST_TOKEN))

    def parse(self, response):
        content = response.body
        records = json.loads(content)
        if len(records) == 0:
            return
        
        for record in records:
            fpath = "scraper/angellist_people_json/%s.json" % record['id']
            with open(fpath, "w") as fh:
                json.dump(record, fh)

