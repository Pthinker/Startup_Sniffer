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

AL_COMPANY_FOLDER = "scraper/scraper/angellist_company_json"
AL_PEOPLE_FOLDER = "scraper/scraper/angellist_people_json"

# API keys
LINKEDIN_API_KEY = "oki2tae9xtf8"
LINKEDIN_SECRET_KEY = "B9W8cKLz44Nj2MzD"

TWITTER_CONSUMER_KEY = "KoNbywN69PbsPmAGPsevpA"
TWITTER_CONSUMER_SECRET = "XyBInKQnJq1dEuTGSU0kbDut17JPQ4hweObhMIUGPzw"
TWITTER_ACCESS_TOKEN = "40215812-GctQUp6lSalxRAu18gW8CHnFk334BlmOeNpny1q4k"
TWITTER_ACCESS_TOKEN_SECRET = "mbTeeO4t3WeSO9xSGt9M98E97ol94TMkfp3ldtEuTA4"

