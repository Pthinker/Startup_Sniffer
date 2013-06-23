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
    name = "angellist_job"
    allowed_domains = ["angel.co"]

    start_urls = []
    session = util.load_session()
    cids = util.get_startup_ids(session)
    session.close()

    for cid in cids:
        start_urls.append("https://api.angel.co/1/startups/%d/jobs?access_token=%s" \
                % (cid, config.ANGELLIST_TOKEN))

    def parse(self, response):
        content = response.body
        records = json.loads(content)
        if len(records) == 0:
            return
        comp_url = response.url
        
        cid = comp_url.split("/")[5]
        fpath = "scraper/angellist_job_json/%s.json" % cid
        with open(fpath, "w") as fh:
            json.dump(records, fh)

