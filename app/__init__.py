from flask import Flask, render_template, g, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from app.models import *
import os

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

metadata = db.MetaData(db.engine)
cb_companies = db.Table('cb_companies', metadata, autoload=True)
db.mapper(CBCompany, cb_companies)
cb_company_info = db.Table('cb_company_info', metadata, autoload=True)
db.mapper(CBCompanyInfo, cb_company_info)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')

@app.before_request
def before_request():
    g.db = db
    g.app = app

@app.route('/')
def index():
    return redirect("/home/index")

@app.route('/about')
def about():
    return render_template("about.html")

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

from app.home.views import mod as homeModule
app.register_blueprint(homeModule)

from app.predict.views import predict_page as predictModule
app.register_blueprint(predictModule)

