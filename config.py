import os

_basedir = os.path.abspath(os.path.dirname(__file__))

# mysql database
DATABASE = 'startup_sniffer'
USERNAME = 'admin'
PASSWORD = 'admin'

# flask
DEBUG = True

SECRET_KEY = 'SecretKeyForSessionSigning'

CSRF_ENABLED = True
CSRF_SESSION_KEY = "somethingimpossibletoguess"

SQLALCHEMY_DATABASE_URI = 'mysql://admin:admin@localhost/startup_sniffer?charset=utf8'
DATABASE_CONNECT_OPTIONS = {}

# json files folders
CB_COMPANY_FOLDER = "scraper/scraper/crunchbase_company_json"
CB_PEOPLE_FOLDER = "scraper/scraper/crunchbase_people_json"
CB_FINANCIAL_FOLDER = "scraper/scraper/crunchbase_financial_json"

# API keys

