from flask import Blueprint, render_template, request, flash
from app import db, cb_companies, al_companies, startup_info, APP_STATIC
from app.models import *
import pickle
import os
import re
import pandas as pd
import numpy as np
import json

predict_page = Blueprint('predict', __name__, url_prefix='/predict')

@predict_page.route('/')
@predict_page.route('/index')
def index():
    records = db.session.query(al_companies).filter(
            ALCompany.logo_url != None).limit(22)
    
    df = pd.read_csv(os.path.join(APP_STATIC, 'predict_com.csv'), 
            header=0, index_col=0)
    comp_json = json.dumps(["%s (%s)" % (df.ix[cid]['name'], cid) for cid in df.index.values])
    return render_template("predict/index.html", comp_json=comp_json, records=records)

@predict_page.route('/analyze/', methods=['POST'])
def analyze():
    records = db.session.query(al_companies).filter(
            ALCompany.logo_url != None).limit(22)
    
    df = pd.read_csv(os.path.join(APP_STATIC, 'predict_com.csv'), 
            header=0, index_col=0)
    comp_json = json.dumps(["%s (%s)" % (df.ix[cid]['name'], cid) for cid in df.index.values])
    
    crunch_id = request.form.get('crunch-id', None)
    if (crunch_id is None) or (len(crunch_id.strip())==0):
        flash('Please input valid startup name')
        return render_template('predict/index.html', comp_json=comp_json, records=records)
    
    matobj = re.search("\((.*)\)", crunch_id)
    if matobj:
        crunch_id = matobj.group(1)
    else:
        crunch_id = None
    
    if crunch_id is None:
        flash('Sorry, the input company is not in our database')
        return render_template('predict/index.html', comp_json=comp_json, records=records)

    model = pickle.load(open(os.path.join(APP_STATIC, 'rf.model')))
    del df['name']
    
    row = np.array(df.ix[crunch_id])
    prob = model.predict_proba(row)
    prob = "%.2f%%" % (prob[0][1]*100.0)
    
    record = db.session.query(cb_companies).filter(
            CBCompany.crunch_id==crunch_id).first()
    
    com_record = db.session.query(cb_companies).filter(
            CBCompany.crunch_id==crunch_id).first()
    
    return render_template("predict/analyze.html", prob=prob, \
            company=record, comp_json=comp_json, com_record=com_record)

