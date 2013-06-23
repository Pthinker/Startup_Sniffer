from flask import Blueprint, render_template, request
from app import db, cb_companies, cb_company_info, APP_STATIC
from app.models import *
import pickle
import os
import pandas as pd
import numpy as np
import json

predict_page = Blueprint('predict', __name__, url_prefix='/predict')

@predict_page.route('/')
@predict_page.route('/index')
def index():
    #records = db.session.query(cb_company_info).filter(CBCompanyInfo.img != None).filter(
    #        CBCompanyInfo.url != None).limit(10)
    
    df = pd.read_csv(os.path.join(APP_STATIC, 'predict_com.csv'), header=0, index_col=0)
    comp_json = json.dumps([cid for cid in df.index.values])
    return render_template("predict/index.html", comp_json=comp_json)

@predict_page.route('/analyze/', methods=['POST'])
def analyze():
    crunch_id = request.form.get('crunch-id', None)

    #TODO: handle None case

    model = pickle.load(open(os.path.join(APP_STATIC, 'rf.model')))
    df = pd.read_csv(os.path.join(APP_STATIC, 'predict_com.csv'), header=0, index_col=0)

    comp_json = json.dumps([cid for cid in df.index.values])
    
    row = np.array(df.ix[crunch_id])
    prob = model.predict_proba(row)

    record = db.session.query(cb_company_info).filter(CBCompanyInfo.crunch_id==crunch_id).first()
    prob = "%.2f%%" % (prob[0][1]*100.0)

    return render_template("predict/analyze.html", prob=prob, company=record, comp_json=comp_json)

