from flask import Flask, render_template, g, redirect, session
from flask.ext.sqlalchemy import SQLAlchemy
from app.models import *
import os

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

metadata = db.MetaData(db.engine)
cb_companies = db.Table('cb_companies', metadata, autoload=True)
db.mapper(CBCompany, cb_companies)
al_companies = db.Table('al_companies', metadata, autoload=True)
db.mapper(ALCompany, al_companies)
cb_company_info = db.Table('cb_company_info', metadata, autoload=True)
db.mapper(CBCompanyInfo, cb_company_info)
startup_info = db.Table('startup_info', metadata, autoload=True)
db.mapper(StartupInfo, startup_info)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')

@app.before_request
def before_request():
    g.db = db
    g.app = app

@app.before_first_request
def before_first_request():
    session['user_oauth_token'] = None
    session['user_oauth_secret'] = None

@app.route('/')
@app.route('/index')
def index():
    return redirect("/home/index")

@app.route('/about')
def about():
    return render_template("about.html")

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def not_found(error):
    return render_template('500.html'), 500

from app.home.views import mod as homeModule
app.register_blueprint(homeModule)

from app.predict.views import predict_page as predictModule
app.register_blueprint(predictModule)

from app.board.views import board_page as boardModule
app.register_blueprint(boardModule)

from app.job.views import job_page as jobModule
app.register_blueprint(jobModule)

