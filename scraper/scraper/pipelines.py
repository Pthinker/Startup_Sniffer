# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from crunchbase_scraper.items import CompanyItem
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class MysqlStorePipeline(object):
    def __init__(self):
        self.engine = create_engine('mysql://admin:admin@localhost/crunchbase?charset=utf8')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    '''
    Depreciated
    '''
    '''
    def process_item(self, item, spider):
        if isinstance(item, CompanyItem):
            com = Company()
            com.name = item['name']
            com.crunch_id = item['crunch_id']
            com.website = item['website'] if 'website' in item else None
            com.blog = item['blog'] if 'blog' in item else None
            com.twitter = item['twitter'] if 'twitter' in item else None
            com.category = item['category'] if 'category' in item else None
            com.email = item['email'] if 'email' in item else None
            com.employee_num = item['employee_num'] if 'employee_num' in item else None
            com.founded = item['founded'] if 'founded' in item else None
            com.desc = item['desc'] if 'desc' in item else None

            self.session.add(com)
            self.session.commit()
    '''

