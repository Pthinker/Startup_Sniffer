# Scrapy settings for crunchbase_scraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'crunchbase_scraper'

SPIDER_MODULES = ['crunchbase_scraper.spiders']
NEWSPIDER_MODULE = 'crunchbase_scraper.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'crunchbase_scraper (+http://www.yourdomain.com)'

ITEM_PIPELINES = [
    #'crunchbase_scraper.pipelines.MysqlStorePipeline',
]
