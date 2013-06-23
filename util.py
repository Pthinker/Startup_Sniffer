from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker

import os
import json
import re
import time
import random

import config
import socialmedia

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


def load_session():
    """Connectiong to exisitng database and return session
    """
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    metadata = MetaData(engine)

    cb_companies = Table('cb_companies', metadata, autoload=True)
    mapper(CBCompany, cb_companies)
    
    cb_exits = Table('cb_exits', metadata, autoload=True)
    mapper(CBExit, cb_exits)

    cb_competitors = Table('cb_competitors', metadata, autoload=True)
    mapper(CBCompetitor, cb_competitors)

    cb_company_people = Table('cb_company_people', metadata, autoload=True)
    mapper(CBCompanyPeople, cb_company_people)

    al_companies = Table('al_companies', metadata, autoload=True)
    mapper(ALCompany, al_companies)

    Session = sessionmaker(bind=engine)
    session = Session()
    
    return session

def exited_competitors_count(crunch_id, session):
    """Return the number of successful competitors of crunch_id
    """
    if crunch_id is None:
        print "crunch_id is None"
        return None

    if session is None:
        print "DB session is None"
        return None
    
    return session.query(CBCompetitor, CBExit).filter(
            CBCompetitor.company==crunch_id).filter(
            CBCompetitor.competitor==CBExit.company).count()

def founded_company_count(crunch_id, session):
    """Return the number of companies founder created
    """
    if crunch_id is None:
        print "crunch_id is None"
        return None

    if session is None:
        print "DB session is None"
        return None

    count = 0
    records = session.query(CBCompanyPeople).filter(
            CBCompanyPeople.company==crunch_id).all()
    
    for record in records:
        title = record.title
        if ("Founder" in title) or ("founder" in title) or ("owner" in title) or \
            ("Owner" in title) or ("Founding" in title) or ("founding" in title):
            pid = record.people
            rows = session.query(CBCompanyPeople).filter(
                    CBCompanyPeople.people==pid).all()
            for row in rows:
                ptitle = row.title
                if ("Founder" in ptitle) or ("founder" in ptitle) or \
                    ("owner" in ptitle) or ("Owner" in ptitle) or \
                    ("Founding" in ptitle) or ("founding" in ptitle):
                    count += 1
    return count

def founded_company_exit_count(crunch_id, session):
    """Return the number of exited companies founder created
    """
    if crunch_id is None:
        print "crunch_id is None"
        return None

    if session is None:
        print "DB session is None"
        return None

    count = 0
    records = session.query(CBCompanyPeople).filter(
            CBCompanyPeople.company==crunch_id).all()
    for record in records:
        title = record.title
        if ("Founder" in title) or ("founder" in title) or ("owner" in title) or \
            ("Owner" in title) or ("Founding" in title) or ("founding" in title):
            pid = record.people
            rows = session.query(CBCompanyPeople).filter(
                    CBCompanyPeople.people==pid).all()
            for row in rows:
                ptitle = row.title
                if ("Founder" in ptitle) or ("founder" in ptitle) or \
                    ("owner" in ptitle) or ("Owner" in ptitle) or \
                    ("Founding" in ptitle) or ("founding" in ptitle):
                    count += session.query(CBExit).filter(CBExit.company==row.company).count()
    return count

def generate_training_data(session):
    # Get companies in categoeis that interested
    categories = ['mobile', 'web', 'advertising', 'ecommerce', 'games_video', \
            'software', 'search']
    companies = session.query(CBCompany).filter(
            CBCompany.category.in_(categories)).all()
    
    fh = open('data/training.csv', "w")
    fh.write("crunch_id,milestone_num,competitor_num,office_num,product_num," + \
             "service_num,founding_round_num,total_money_raised,acquisition_num," + \
             "investment_num,vc_num,num_exited_competitor,company_count," + \
             "exited_company_count,success\n")
    
    for company in companies:
        crunch_id = company.crunch_id
        exit_record = session.query(CBExit).filter(
                CBExit.company==crunch_id).first()
        if exit_record is None: # Negative instances
            if company.founded_year is not None and company.founded_year<2009:
                success = 0
                amount = None
            else:
                continue
        else: # positive instances
            success = 1
            amount = exit_record.valuation

        num_exited_competitor = exited_competitors_count(
                company.crunch_id, session)
        
        company_count = founded_company_count(company.crunch_id, session)

        exited_company_count = founded_company_exit_count(
                company.crunch_id, session)

        total_money_raised = float(company.total_money_raised) / 10000000.0
        success = 1 if company.success==1 else 0
        fh.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%d,%d,%d,%s\n" % \
                  (company.crunch_id, company.milestone_num, \
                   company.competitor_num, company.office_num, \
                   company.product_num, company.service_num, \
                   company.founding_round_num, total_money_raised, \
                   company.acquisition_num, company.investment_num, \
                   company.vc_num, num_exited_competitor, company_count, \
                   exited_company_count, success))
    fh.close()

def generate_testing_data(session):
    # Get companies in categoeis that interested
    categories = ['mobile', 'web', 'advertising', 'ecommerce', 'games_video', \
            'software', 'search', 'other']
    companies = session.query(CBCompany).filter(
            CBCompany.category.in_(categories)).filter(
            CBCompany.founded_year>=2007).all()
    
    fh = open('data/predict_com.csv', "w")
    fh.write("crunch_id,milestone_num,competitor_num,office_num,product_num,service_num," + \
             "founding_round_num,total_money_raised,acquisition_num,investment_num,vc_num," + \
             "num_exited_competitor,company_count,exited_company_count\n")

    for company in companies:
        crunch_id = company.crunch_id
        
        num = session.query(CBExit).filter(CBExit.company==crunch_id).count()
        if num > 0:
            continue

        num_exited_competitor = exited_competitors_count(
                company.crunch_id, session)
        
        company_count = founded_company_count(company.crunch_id, session)

        exited_company_count = founded_company_exit_count(
                company.crunch_id, session)

        total_money_raised = float(company.total_money_raised) / 10000000.0
        
        fh.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%d,%d,%d\n" % \
                  (company.crunch_id, company.milestone_num, \
                   company.competitor_num, company.office_num, \
                   company.product_num, company.service_num, \
                   company.founding_round_num, total_money_raised, \
                   company.acquisition_num, company.investment_num, \
                   company.vc_num, num_exited_competitor, \
                   company_count, exited_company_count))
    fh.close()

def get_startup_ids(session):
    al_startups = session.query(ALCompany).all()
    ids = []
    for startup in al_startups:
        ids.append(startup.angellist_id)
    return ids

def get_new_startups(session):
    categories = ['mobile', 'web', 'advertising', 'ecommerce', 'games_video', \
            'software', 'search', 'other']
    
    cb_startups = session.query(CBCompany).filter(
            CBCompany.category.in_(categories)).filter(
            CBCompany.founded_year>2012).all()

    al_startups = session.query(ALCompany).filter(
            ALCompany.company_type=='Startup').all()

    for al_startup in al_startups:
        if session.query(CBCompany).filter(
                CBCompany.name==al_startup.name).count() > 0:
            pass
        else:
            print al_startup.name

def update_bity_hash(session):
    """ Save bitly.com url hash for each startup company
    """
    al_startups = session.query(ALCompany).filter(
            ALCompany.company_url is not None).all()
    for startup in al_startups:
        if startup.bitly_hash is not None:
            continue 

        bitly_hash = socialmedia.get_bitly_hash(startup.company_url)
        
        if bitly_hash is not None:
            startup.bitly_hash = bitly_hash
            session.add(startup)
        else:
            print "%s, %s hash is none" % (startup.name, startup.id)

    session.commit()

def main():
    session = load_session()
    
    #generate_training_data(session)
    #generate_testing_data(session)
    
    #get_new_startups(session)
    
    #get_startup_ids(session)

    update_bity_hash(session)

    session.close()

if __name__ == "__main__":
    main()

