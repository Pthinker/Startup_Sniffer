from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.sql import or_, and_

import os
import json
import re

import config

class CBCompany(object):
    pass

class CBCompanyInfo(object):
    pass

class CBPeople(object):
    pass

class CBCompanyPeople(object):
    pass

class CBCompetitor(object):
    pass

class CBFinancial(object):
    pass

class CBExit(object):
    pass

class CBFunding(object):
    pass

class ALCompany(object):
    pass

class ALPeople(object):
    pass

def get_company():
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    metadata = MetaData(engine)

    cb_companies = Table('cb_companies', metadata, autoload=True)
    mapper(CBCompany, cb_companies)
    
    Session = sessionmaker(bind=engine)
    session = Session()

    #terms = ['mobile', 'web', 'advertising', 'ecommerce', 'games_video', 'software', 'search', 'network_hosting']
    terms = ['mobile']
    companies = session.query(CBCompany).filter(CBCompany.category=='mobile').all()
    fh = open('companies.csv', "w")
    fh.write("crunch_id,milestone_num,competitor_num,office_num,product_num,service_num,founding_round_num,total_money_raised,acquisition_num,investment_num,vc_num,success\n")
    for company in companies:
        total_money_raised = float(company.total_money_raised) / 10000000.0
        success = 1 if company.success==1 else 0
        fh.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % \
                  (company.crunch_id, company.milestone_num, \
                   company.competitor_num, company.office_num, company.product_num, company.service_num, \
                   company.founding_round_num, total_money_raised, company.acquisition_num, \
                   company.investment_num, company.vc_num, success))
    fh.close()

    session.close()

def main():
    get_company()

if __name__ == "__main__":
    main()

