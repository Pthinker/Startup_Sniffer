from sqlalchemy import create_engine, Column, Table, MetaData, ForeignKey
from sqlalchemy import Integer, String, Text, Numeric, Boolean, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import simplejson as json
import os
import re
from datetime import datetime

import config

engine = create_engine('mysql://admin:admin@localhost/startup_sniffer?charset=utf8', echo=False)
Base = declarative_base()

class Company(Base):
    __tablename__ = 'cb_companies'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    url = Column(String(250))
    crunch_id = Column(String(200), nullable=False, index=True, unique=True)
    twitter = Column(String(30))
    category = Column(String(30))
    employee_num = Column(Integer)
    founded_year = Column(Integer)
    founded_month = Column(Integer)
    dead_year = Column(Integer)
    dead_month = Column(Integer)
    
    milestone_num = Column(Integer)
    competitor_num = Column(Integer)
    office_num = Column(Integer)
    product_num = Column(Integer)
    service_num = Column(Integer) # number of service providers
    
    founding_round_num = Column(Integer)
    total_money_raised = Column(Numeric)
    acquisition_num = Column(Integer) # number of companies it acquired
    investment_num = Column(Integer) # number of investments it made
    vc_num = Column(Integer) # number of VC and provate equitity firms investing

    success = Column(Boolean)

class CompanyInfo(Base):
    __tablename__ = 'cb_company_info'
    
    id = Column(Integer, primary_key=True)
    crunch_id = Column(String(200), nullable=False, index=True, unique=True)
    name = Column(String(250), nullable=False)
    url = Column(String(250))
    twitter = Column(String(30))
    img = Column(String(200))
    category = Column(String(30))
    tags = Column(String(200))
    desc = Column(String(100))
    overview = Column(Text)

class People(Base):
    __tablename__ = 'cb_people'

    id = Column(Integer, primary_key=True)
    crunch_id = Column(String(200), nullable=False, index=True, unique=True)
    first_name = Column(String(50))
    last_name = Column(String(150))
    twitter = Column(String(50))
    tags = Column(String(300))
    overview = Column(Text)

class CompanyPeople(Base):
    __tablename__ = 'cb_company_people'
    
    id = Column(Integer, primary_key=True)
    company = Column(String(200), ForeignKey("cb_companies.crunch_id", ondelete='CASCADE'))
    organization = Column(String(200), ForeignKey("cb_financial_organizations.crunch_id", ondelete='CASCADE'))
    people = Column(String(200), ForeignKey("cb_people.crunch_id", ondelete='CASCADE'), nullable=False)
    is_past = Column(Boolean)
    title = Column(String(150))

class CompanyCompetitor(Base):
    __tablename__ = 'cb_competitors'
    
    id = Column(Integer, primary_key=True)
    company = Column(String(200), ForeignKey("cb_companies.crunch_id", ondelete='CASCADE'), nullable=False)
    competitor = Column(String(200), ForeignKey("cb_companies.crunch_id", ondelete='CASCADE'), nullable=False)

class FinancialOrg(Base):
    __tablename__ = 'cb_financial_organizations'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    crunch_id = Column(String(200), nullable=False, index=True, unique=True)
    url = Column(String(200))
    twitter = Column(String(30))
    desc = Column(String(250))
    employee_num = Column(Integer)
    founded_year = Column(Integer)
    founded_month = Column(Integer)
    tags = Column(String(300))
    overview = Column(Text)

class Exit(Base):
    __tablename__ = 'cb_exits'

    id = Column(Integer, primary_key=True)
    company = Column(String(200), ForeignKey("cb_companies.crunch_id", ondelete='CASCADE'))
    acquired_by = Column(String(200))
    valuation = Column(Float)
    currency = Column(String(10))
    year = Column(Integer)
    month = Column(Integer)

class Funding(Base):
    __tablename__ = 'cb_fundings'

    id = Column(Integer, primary_key=True)
    company = Column(String(200), ForeignKey("cb_companies.crunch_id", ondelete='CASCADE'), nullable=False) # company receiving the funding
    round_code = Column(String(20))
    amount = Column(Numeric)
    currency = Column(String(10))
    year = Column(Integer)
    month = Column(Integer)

class FundingMember(Base):
    __tablename__ = 'cb_funding_members'
    id = Column(Integer, primary_key=True)
    funding = Column(Integer, ForeignKey("cb_fundings.id", ondelete='CASCADE'), nullable=False)
    company = Column(String(200), ForeignKey("cb_companies.crunch_id", ondelete='CASCADE'))
    financial = Column(String(200), ForeignKey("cb_people.crunch_id", ondelete='CASCADE'))
    people = Column(String(200), ForeignKey("cb_financial_organizations.crunch_id", ondelete='CASCADE'))

class AngellistCompany(Base):
    __tablename__ = 'al_companies'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), index=True)
    angellist_id = Column(Integer)
    angellist_url = Column(String(100))
    logo_url = Column(String(150))
    quality = Column(Integer)
    product_desc = Column(Text)
    desc = Column(Text)
    follower_count = Column(Integer)
    company_url = Column(String(100))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    twitter_url = Column(String(100))
    categories = Column(String(200))
    company_type = Column(String(100))
    locations = Column(String(100))

class AngellistPeople(Base):
    __tablename__ = 'al_people'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), index=True)
    bio = Column(Text)
    angellist_id = Column(Integer)
    angellist_url = Column(String(100))
    image = Column(String(200))
    follower_count = Column(Integer)
    linkedin_url = Column(String(200))
    twitter_url = Column(String(150))
    facebook_url = Column(String(150))
    roles = Column(String(200))
    investor = Column(Boolean)
    locations = Column(String(100))


def store_cb_companies():
    Session = sessionmaker(bind=engine)
    session = Session()
    
    files = os.listdir(config.CB_COMPANY_FOLDER)

    for fname in files:
        fpath = os.path.join(config.CB_COMPANY_FOLDER, fname)
        with open(fpath) as fh:
            com_dict = json.load(fh, strict=False)
            
        com = Company()
        com.name = com_dict['name']
        com.url = com_dict['homepage_url']
        com.crunch_id = com_dict['permalink']
        com.twitter = com_dict['twitter_username']
        com.category = com_dict['category_code']
        com.employee_num = com_dict['number_of_employees']
        com.founded_year = com_dict['founded_year']
        com.founded_month = com_dict['founded_month']
        com.dead_year = com_dict['deadpooled_year']
        com.dead_month = com_dict['deadpooled_month']
            
        money = com_dict['total_money_raised']
        matobj = re.search(r"([\d\.]+)", money)
        if matobj:
            num = matobj.group(1)
            if money[-1].upper() == 'M':
                money = float(num) * 1000000
            elif money[-1].upper() == 'B':
                money = float(num) * 1000000000
            elif money[-1].upper() == 'K':
                money = float(num) * 1000
            else:
                money = float(num)
            com.total_money_raised = money
        
        com.milestone_num = len(com_dict['milestones'])
        com.competitor_num = len(com_dict['competitions'])
        com.office_num = len(com_dict['offices'])
        com.product_num = len(com_dict['products'])
        com.service_num = len(com_dict['providerships'])
        com.founding_round_num = len(com_dict['funding_rounds'])
        com.acquisition_num = len(com_dict['acquisitions'])
        com.investment_num = len(com_dict['investments'])
        
        num = 0
        if com_dict['funding_rounds'] is not None:
            for funding_round in com_dict['funding_rounds']:
                num += len(funding_round['investments'])
        com.vc_num = num

        if com_dict['ipo'] is not None or com_dict['acquisition'] is not None:
            com.success = True

        session.add(com)
    session.commit()
    session.close()

def store_cb_company_info():
    Session = sessionmaker(bind=engine)
    session = Session()
    
    files = os.listdir(config.CB_COMPANY_FOLDER)

    for fname in files:
        fpath = os.path.join(config.CB_COMPANY_FOLDER, fname)
        with open(fpath) as fh:
            com_dict = json.load(fh, strict=False)
            
        com = CompanyInfo()
        com.name = com_dict['name']
        com.crunch_id = com_dict['permalink']
        com.url = com_dict['homepage_url']
        com.twitter = com_dict['twitter_username']
        com.category = com_dict['category_code']
        com.desc = com_dict['description']
        com.overview = com_dict['overview']
        com.tags = com_dict['tag_list']
        if com_dict['image'] is not None and len(com_dict['image']['available_sizes'])>0:
            com.img = com_dict['image']['available_sizes'][-1][1]
        session.add(com)
    session.commit()
    session.close()

def store_cb_people():
    Session = sessionmaker(bind=engine)
    session = Session()
    
    files = os.listdir(config.CB_PEOPLE_FOLDER)
    for fname in files:
        fpath = os.path.join(config.CB_PEOPLE_FOLDER, fname)
        with open(fpath) as fh:
            pdict = json.load(fh, strict=False)
        p = People()
        p.crunch_id = pdict['permalink']
        p.first_name = pdict['first_name']
        p.last_name = pdict['last_name']
        p.twitter = pdict['twitter_username']
        p.tags = pdict['tag_list']
        p.overview = pdict['overview']
        session.add(p)
    session.commit()
    session.close()

def store_cb_financial_organizations():
    Session = sessionmaker(bind=engine)
    session = Session()
    
    org_files = os.listdir(config.CB_FINANCIAL_FOLDER)
    for fname in org_files:
        fpath = os.path.join(config.CB_FINANCIAL_FOLDER, fname)
        with open(fpath) as fh:
            org_dict = json.load(fh, strict=False)

        org = FinancialOrg()
        org.name = org_dict['name']
        org.crunch_id = org_dict['permalink']
        org.url = org_dict['homepage_url']
        org.twitter = org_dict['twitter_username']
        org.desc = org_dict['description']
        org.employee_num = org_dict['number_of_employees']
        org.founded_year = org_dict['founded_year']
        org.founded_month = org_dict['founded_month']
        org.tags = org_dict['tag_list']
        org.overview = org_dict['overview']
        
        session.add(org)
    session.commit()
    session.close()

def store_cb_companypeople():
    Session = sessionmaker(bind=engine)
    session = Session()
    
    pdict = {}
    for people in session.query(People):
        pdict[people.crunch_id] = 1

    company_folder = config.CB_COMPANY_FOLDER
    company_files = os.listdir(company_folder)
    for fname in company_files:
        fpath = os.path.join(company_folder, fname)
        with open(fpath) as fh:
            com_dict = json.load(fh, strict=False)

        com_id = com_dict['permalink']
        for rec in com_dict['relationships']:
            if not rec['person']['permalink'] in pdict:
                continue
            compeo = CompanyPeople()
            compeo.company = com_id
            compeo.is_past = rec['is_past']
            compeo.title = rec['title']
            compeo.people = rec['person']['permalink']
            session.add(compeo)
    session.commit()

    folder = config.CB_FINANCIAL_FOLDER
    files = os.listdir(folder)
    for fname in files:
        fpath = os.path.join(folder, fname)
        with open(fpath) as fh:
            org_dict = json.load(fh, strict=False)
        
        org_id = org_dict['permalink']
        
        for rec in org_dict['relationships']:
            if not rec['person']['permalink'] in pdict:
                continue
            compeo = CompanyPeople()
            compeo.organization = org_id
            compeo.is_past = rec['is_past']
            compeo.title = rec['title']
            compeo.people = rec['person']['permalink']
            
            session.add(compeo)
    session.commit()
    session.close()

def store_cb_competitors():
    Session = sessionmaker(bind=engine)
    session = Session()
    
    company_folder = config.CB_COMPANY_FOLDER
    company_files = os.listdir(company_folder)
    for fname in company_files:
        fpath = os.path.join(company_folder, fname)
        with open(fpath) as fh:
            com_dict = json.load(fh, strict=False)

        com_id = os.path.splitext(fname)[0]
        for rec in com_dict['competitions']:
            comp = CompanyCompetitor()
            comp.company = com_id
            comp.competitor = rec['competitor']['permalink']
            session.add(comp)
    session.commit()
    session.close()

def store_cb_fundings():
    Session = sessionmaker(bind=engine)
    session = Session()
    
    folder = config.CB_COMPANY_FOLDER
    company_files = os.listdir(folder)
    for fname in company_files:
        fpath = os.path.join(folder, fname)
        with open(fpath) as fh:
            com_dict = json.load(fh, strict=False)

        for rec in com_dict['funding_rounds']:
            funding = Funding()
            funding.company = com_dict['permalink']
            funding.round_code = rec['round_code']
            funding.amount = rec['raised_amount']
            funding.currency = rec['raised_currency_code']
            funding.year = rec['funded_year']
            funding.month = rec['funded_month']
            
            session.add(funding)
            session.flush()
            
            for member in rec['investments']:
                mem = FundingMember()
                mem.funding = funding.id
                if member['company'] is not None:
                    mem.company = member['company']['permalink']

                if member['financial_org'] is not None:
                    funding.financial = member['financial_org']['permalink']
            
                if member['person'] is not None:
                    funding.people = member['person']['permalink']
                
                session.add(mem)
    session.commit()

def store_cb_exits():
    Session = sessionmaker(bind=engine)
    session = Session()
    
    company_folder = config.CB_COMPANY_FOLDER
    company_files = os.listdir(company_folder)
    for fname in company_files:
        fpath = os.path.join(company_folder, fname)
        with open(fpath) as fh:
            com_dict = json.load(fh, strict=False)

        if com_dict['acquisition'] is not None:
            rec = com_dict['acquisition']
            exit = Exit()
            exit.company = com_dict['permalink']
            exit.acquiring_company = rec['acquiring_company']['permalink']
            exit.amount = rec['price_amount']
            exit.currency = rec['price_currency_code']
            exit.year = rec['acquired_year']
            exit.month = rec['acquired_month']
            session.add(exit)
        elif com_dict['ipo'] is not None:
            rec = com_dict['ipo']
            exit = Exit()
            exit.company = com_dict['permalink']
            exit.amount = rec['valuation_amount']
            exit.currency = rec['valuation_currency_code']
            exit.year = rec['pub_year']
            exit.month = rec['pub_month']
            session.add(exit)
    session.commit()
    session.close()

def store_cb_ipo():
    Session = sessionmaker(bind=engine)
    session = Session()
    
    company_folder = "%s/company_json" % json_folder
    company_files = os.listdir(company_folder)
    for fname in company_files:
        fpath = os.path.join(company_folder, fname)
        with open(fpath) as fh:
            com_dict = json.load(fh, strict=False)
        if com_dict['ipo'] is not None:
            ipo = IPO()
            rec = com_dict['ipo']
            ipo.company = com_dict['permalink']
            ipo.valuation = rec['valuation_amount']
            ipo.year = rec['pub_year']
            ipo.month = rec['pub_month']
            ipo.day = rec['pub_day']
            session.add(ipo)
    session.commit()
    session.close()

def store_cb_acquisition():
    Session = sessionmaker(bind=engine)
    session = Session()
    
    cdict = {}
    for com in session.query(Company):
        cdict[com.crunch_id] = 1

    company_folder = "%s/company_json" % json_folder
    company_files = os.listdir(company_folder)
    for fname in company_files:
        fpath = os.path.join(company_folder, fname)
        with open(fpath) as fh:
            com_dict = json.load(fh, strict=False)
        if com_dict['acquisition'] is not None:
            rec = com_dict['acquisition']
            if not rec['acquiring_company']['permalink'] in cdict:
                continue
            acq = Acquisition()
            acq.company = com_dict['permalink']
            acq.acquiring_company = rec['acquiring_company']['permalink']
            acq.amount = rec['price_amount']
            acq.currency = rec['price_currency_code']
            acq.year = rec['acquired_year']
            acq.month = rec['acquired_month']
            acq.day = rec['acquired_day']
            
            session.add(acq)

    session.commit()
    session.close()

def store_al_company():
    Session = sessionmaker(bind=engine)
    session = Session()

    company_folder = config.AL_COMPANY_FOLDER
    company_files = os.listdir(company_folder)
    for fname in company_files:
        fpath = os.path.join(company_folder, fname)
        with open(fpath) as fh:
            com_dict = json.load(fh, strict=False)
         
        com = AngellistCompany()
        com.name = com_dict['name']
        com.angellist_id = com_dict['id']
        com.angellist_url = com_dict['angellist_url']
        com.logo_url = com_dict['logo_url']
        com.quality = com_dict['quality']
        com.product_desc = com_dict['product_desc']
        com.desc = com_dict['high_concept']
        com.follower_count = com_dict['follower_count']
        com.company_url = com_dict['company_url']
            
        created_at = com_dict['created_at'].split("T")[0]
        com.created_at = datetime.strptime(created_at, "%Y-%m-%d")
            
        updated_at = com_dict['updated_at'].split("T")[0]
        com.updated_at = datetime.strptime(updated_at, "%Y-%m-%d")
            
        com.twitter_url = com_dict['twitter_url']

        categories = com_dict['markets']
        arr = []
        for cat in categories:
            arr.append(cat['display_name'])
        com.categories = ",".join(arr)

        company_types = com_dict['company_type']
        arr = []
        for com_type in company_types:
            arr.append(com_type['display_name'])
        com.company_type = ",".join(arr)
        
        locations = com_dict['locations']
        arr = []
        for location in locations:
            arr.append(location['name'])
        com.locations = ",".join(arr)

        session.add(com)

    session.commit()
    session.close()

def store_al_people():
    Session = sessionmaker(bind=engine)
    session = Session()

    people_folder = config.AL_PEOPLE_FOLDER
    people_files = os.listdir(people_folder)
    for fname in people_files:
        fpath = os.path.join(people_folder, fname)
        with open(fpath) as fh:
            com_dict = json.load(fh, strict=False)
         
        com = AngellistPeople()
        com.angellist_id = com_dict['id']
        com.name = com_dict['name']
        com.angellist_url = com_dict['angellist_url']
        com.image = com_dict['image']
        com.bio = com_dict['bio']
        com.follower_count = com_dict['follower_count']
        com.twitter_url = com_dict['twitter_url']
        com.facebook_url = com_dict['facebook_url']
        com.linkedin_url = com_dict['linkedin_url']
        com.investor = com_dict['investor']

        roles = com_dict['roles']
        arr = []
        for role in roles:
            arr.append(role['display_name'])
        com.roles = ",".join(arr)

        locations = com_dict['locations']
        arr = []
        for location in locations:
            arr.append(location['name'])
        com.locations = ",".join(arr)

        session.add(com)

    session.commit()
    session.close()


def main():
    Base.metadata.create_all(engine)

    '''
    # crunchbase data
    print "Store companies info"
    store_cb_company_info()
    
    print "Store companies"
    store_cb_companies()
 
    print "Store people"
    store_cb_people()
    
    print "Store financial organizations"
    store_cb_financial_organizations()       
    
    print "Store competitors"
    store_cb_competitors()
    
    print "Store company people"
    store_cb_companypeople()

    print "Store funding rounds"
    store_cb_fundings()

    print "Store Exits"
    store_cb_exits()
    
    '''

    # AngelList data
    print "Store angellist company"
    store_al_company()
    print "Store angellist people"
    store_al_people()

if __name__ == "__main__":
    main()

