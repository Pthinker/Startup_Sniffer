from flask import Blueprint, render_template, request
from app import db, cb_companies, cb_company_info, APP_STATIC
from app.models import *
import pickle
import os
import pandas as pd
import numpy as np

predict_page = Blueprint('predict', __name__, url_prefix='/predict')

@predict_page.route('/')
@predict_page.route('/index')
def index():
    return render_template("predict/index.html")

@predict_page.route('/analyze/', methods=['GET', 'POST'])
def analyze():
    crunch_id = request.form['crunch_id']
    model = pickle.load(open(os.path.join(APP_STATIC, 'mobile.model')))
    df = pd.read_csv(os.path.join(APP_STATIC, 'mobile.csv'), header=0, index_col=0)
    row = np.array(df.ix[crunch_id])
    prob = model.predict_proba(row[:-1])

    record = db.session.query(cb_company_info).filter(CBCompanyInfo.crunch_id==crunch_id).first()
    prob = "%.2f%%" % (prob[0][1]*100.0)

    return render_template("predict/analyze.html", prob=prob, company=record)

