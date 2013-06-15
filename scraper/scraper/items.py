# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class CompanyItem(Item):
    name = Field()
    crunch_id = Field()
    twitter = Field()
    category = Field()
    employee_num = Field()
    founded = Field()
    desc = Field()
    tags = Field()
    overview = Field()
    total_money_raised = Field()
    country = Field()

class PersonItem(Item):
    name = Field()

class FinancialOrgItem(Item):
    name = Field()
    crunch_id = Field()
    twitter = Field()
    desc = Field()
    tags = Field()
    overview = Field()

class FundingItem(Item):
    round_code = Field()
    amount = Field()
    currency = Field()
    funded_year = Field()
    funded_month = Field()
    funded_day = Field()
    company = Field()
    sources = Field()

