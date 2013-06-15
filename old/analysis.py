import numpy as np
import matplotlib.pyplot as plt
from pylab import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
import operator
from db import Company, Investment, IPO, Investment, Acquisition, People, CompanyPeople


engine = create_engine('mysql://admin:admin@localhost/crunchbase?charset=utf8')
Session = sessionmaker(bind=engine)

colors = ['#348ABD', '#A60628']

def company_year_bar():
    session = Session()
    numbers = []
    for yr in range(1995, 2013):
        numbers.append(session.query(Company).filter(Company.founded==yr).count())

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111)
    ax.bar(range(1995, 2013), numbers, color=colors[0], edgecolor=colors[0], align="center", width=0.8, alpha=0.6, lw=2)
    ax.grid(True)
    ax.set_xlabel('Year')
    ax.set_ylabel('# of founded companies')
    ax.set_title('Number of founded tech companies per year since between 1995 and 2012');
    plt.savefig("plots/company_year_bar.pdf")
    plt.show()

def company_category_bar(year=2012):
    session = Session()
    companies = session.query(Company).filter(Company.founded==str(year))
    category_count = {}
    for com in companies:
        cat = com.category
        if cat is not None:
            category_count[cat] = category_count.get(cat, 0) + 1
    sorted_cat = sorted(category_count.iteritems(), key=operator.itemgetter(1))
    categories = []
    counts = []
    for cat, count in sorted_cat:
        categories.append(cat)
        counts.append(count)

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111)
    pos = np.arange(len(categories)) + .5

    ax.barh(pos, counts, color=colors[0], edgecolor=colors[0], align="center", alpha=0.6, lw=2)
    ax.set_yticks(pos)
    ax.set_yticklabels(categories)

    ax.grid(True)

    ax.set_xlabel('# of companies')
    ax.set_ylabel('Category')
    ax.set_title("Tech trend in %d" % year)
    plt.savefig("plots/tech_trend_%d.pdf" % year)
    plt.show()

def company_category_year_plot():
    session = Session() 
    
    category_count = {'web':[], 'software':[], 'mobile':[], 'advertising':[], 'education':[], 'biotech':[]}
    for category in category_count:
        for yr in range(1995, 2013):
            category_count[category].append(session.query(Company).filter(Company.category==category, Company.founded==yr).count())

    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111)
    
    for category in category_count:
        ax.plot(range(1995, 2013), category_count[category], label=category, lw=2, alpha=0.6)

    ax.legend(loc=2)
    ax.grid(True)

    ax.set_xlabel('Year')
    ax.set_ylabel('# of founded companies')
    ax.set_title("Company category trend")
    plt.savefig("plots/category_trend.pdf")
    plt.show()

def organization_investment_piechart(org="google-ventures", year=2012):
    # intel-capital, sv-angel, google-ventures
    session = Session()
    
    com_cat = {}
    for com in session.query(Company).filter(Company.category!=None):
        com_cat[com.crunch_id] = com.category

    org_invests = session.query(Investment).filter(Investment.org_source==org, Investment.year==str(year))
    
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111)
    cat_count = {}
    for invest in org_invests:
        if invest.company in com_cat and com_cat[invest.company] != None:
            cat_count[com_cat[invest.company]] = cat_count.get(com_cat[invest.company], 0) + 1
    total = 0
    for cat in cat_count:
        total += cat_count[cat]
    frac = [float(cat_count[c])/total for c in cat_count]
    labels = [c for c in cat_count]
    ax.pie(frac, labels=labels)
    plt.savefig("plots/%s_%s_invest_piechart.pdf" % (org, str(year)))
    plt.show()

def profit_loss():
    session = Session()

    ipos = session.query(IPO).filter(IPO.valuation!=None)
    ipo_values = []
    invest_values = []
    for ipo in ipos:
        invest_value = session.query(func.sum(Investment.amount).label('total')).filter(Investment.company==ipo.company).first().total
        if invest_value is not None:
            ipo_values.append(ipo.valuation)
            invest_values.append(float(invest_value))
    ipo_values = np.array(ipo_values)
    invest_values = np.array(invest_values)

    acqs = session.query(Acquisition).filter(Acquisition.amount!=None)
    acq_values = []
    acq_invest_values = []
    for acq in acqs:
        invest_value = session.query(func.sum(Investment.amount).label('total')).filter(Investment.company==acq.company).first().total
        if invest_value is not None:
            acq_values.append(acq.amount)
            acq_invest_values.append(float(invest_value))
    acq_values = np.array(acq_values)
    acq_invest_values = np.array(acq_invest_values)

    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111)
    ax.grid(True)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Total funding raised before exit')
    ax.set_ylabel('IPO valuation / Acquisition amount')
    ax.plot(invest_values, ipo_values, 'o', color='green', alpha=0.8, markersize=10, label="IPO")
    ax.plot(acq_invest_values, acq_values, 'o', color='blue', alpha=0.8, markersize=10, label="Acquisition")
    ax.legend()
    plt.savefig("plots/profit_loss.pdf")
    plt.show()

def if_collegue(session, p1, p2):
    p1_com = []
    for com_peo in session.query(CompanyPeople).filter(CompanyPeople.people==p1.people):
        p1_com.append(com_peo.company)
    p2_com = []
    for com_peo in session.query(CompanyPeople).filter(CompanyPeople.people==p2.people):
        p2_com.append(com_peo.company)
    return bool(set(p1_com) & set(p2_com))
    

def people_network(cat='mobile', year=2012):
    session = Session()
    companies = session.query(Company).filter(Company.category==cat, Company.founded==year)
    persons = []
    for com in companies:
        com_people = session.query(CompanyPeople).filter(CompanyPeople.company==com.crunch_id, CompanyPeople.is_past==False)
        persons.extend(com_people)
    ofh = open("%s_%s_graph.gexf" % (cat, str(year)), "w")
    ofh.write('''<gexf xmlns:viz="http:///www.gexf.net/1.1draft/viz" xmlns="http://www.gexf.net/1.1draft" version="1.1">\n''')
    ofh.write('''<graph defaultedgetype="undirected">\n''')

    ofh.write('<nodes count="%d">\n' % len(persons))
    for p in persons:
        ofh.write('<node id="%s" lable=" ">\n' % p.people)
        ofh.write('<viz:size value="1"/>\n')
        ofh.write('</node>')
    ofh.write('</nodes>\n')
    
    i = 0
    edges_text = ""
    for p1 in persons:
        for p2 in persons:
            if p2.people != p1.people:
                if if_collegue(session, p1, p2):
                    edges_text += '<edge id="%d" source="%s" target="%s" weight="1.0"/>\n' % (i, p1.people, p2.people)
                    i += 1

    ofh.write('<edges count = "%d">\n' % i)
    ofh.write(edges_text)

    ofh.write("</edges>\n")
    ofh.write("</graph>\n")
    ofh.write("</gexf>")

    ofh.close()


def main():
    #company_year_bar()

    #company_category_bar(2012)
 
    #company_category_year_plot()

    #organization_investment_piechart("google-ventures", year=2009)

    #profit_loss()

    people_network(cat='mobile', year=2012)


if __name__ == "__main__":
    main()

