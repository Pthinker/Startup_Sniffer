from flask import Flask, session, flash, request
from flask import redirect, url_for, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from models import *
import os
import re
import socket
from flask_oauth import OAuth
import pandas as pd
import numpy as np
import pickle
import json
from datetime import date, timedelta
import time

import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
metadata = db.MetaData(db.engine)
cb_companies = db.Table('cb_companies', metadata, autoload=True)
db.mapper(CBCompany, cb_companies)
al_companies = db.Table('al_companies', metadata, autoload=True)
db.mapper(ALCompany, al_companies)
startup_info = db.Table('startup_info', metadata, autoload=True)
db.mapper(StartupInfo, startup_info)

oauth = OAuth()
linkedin = oauth.remote_app(
    base_url = 'http://api.linkedin.com/v1/',
    name = 'linkedin',
    consumer_key = app.config['LINKEDIN_API_KEY'],
    consumer_secret = app.config['LINKEDIN_SECRET_KEY'],
    request_token_url = 'https://api.linkedin.com/uas/oauth/requestToken?scope=r_fullprofile',
    access_token_url = 'https://api.linkedin.com/uas/oauth/accessToken',
    authorize_url = 'https://www.linkedin.com/uas/oauth/authenticate')

@app.before_first_request
def before_first_request():
    session['user_oauth_token'] = None
    session['user_oauth_secret'] = None

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/slides')
def slides():
    return render_template("slides.html")

@app.route('/slideshare')
def slideshare():
    return render_template("slideshare.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def not_found(error):
    return render_template('500.html'), 500

@app.route('/board')
def board():
    # Get latest metric data
    records = db.session.query(StartupInfo, ALCompany).filter(
            StartupInfo.al_id==ALCompany.angellist_id).filter(
            StartupInfo.info_date==date.today()).all()
    
    if len(records) == 0:
        records = db.session.query(StartupInfo, ALCompany).filter(
            StartupInfo.al_id==ALCompany.angellist_id).filter(
            StartupInfo.info_date==(date.today()-timedelta(1))).all()
    
    # Get past metric data to compute trend
    past_records = db.session.query(StartupInfo, ALCompany).filter(
            StartupInfo.al_id==ALCompany.angellist_id).filter(
            StartupInfo.info_date==(date.today()-timedelta(5))).all()

    # Find maximum number of each tracking metric
    data = {"angellist":0, "twitter":0, 'bitly':0}
    for record in records:
        al_follower = record.StartupInfo.al_follower
        twitter = record.StartupInfo.twitter_follower
        bitly = record.StartupInfo.bitly_click
        
        if al_follower > data['angellist']:
            data['angellist'] = al_follower
        if twitter > data['twitter']:
            data['twitter'] = twitter
        if bitly > data['bitly']:
            data['bitly'] = bitly
    
    # Cache past data
    past_data = {}
    for record in past_records:
        al_follower = record.StartupInfo.al_follower
        al_quality = record.StartupInfo.al_quality
        twitter = record.StartupInfo.twitter_follower
        bitly = record.StartupInfo.bitly_click
        al_id = record.StartupInfo.al_id
        past_data[al_id] = [al_follower, al_quality, twitter, bitly]

    # Normalize latest data to rank startups and compute trend at the
    # same time 
    ranked_list = {}
    trend_list = {}
    for record in records:
        al_follower = record.StartupInfo.al_follower
        al_quality = record.StartupInfo.al_quality
        twitter = record.StartupInfo.twitter_follower
        bitly = record.StartupInfo.bitly_click
        al_id = record.StartupInfo.al_id
        name = record.ALCompany.name
        img = record.ALCompany.logo_url

        # rank
        nor_al_follower = (al_follower / float(data['angellist'])) * 100.0
        nor_al_quality = al_quality * 10.0
        nor_bitly = (bitly / float(data['bitly'])) * 100.0
        nor_twitter = (twitter / float(data['twitter'])) * 100.0
        score = 0.25 * nor_al_follower + 0.25 * nor_al_quality + \
                0.25 * nor_bitly + 0.25 * nor_twitter
        
        ranked_list[al_id] = {}
        ranked_list[al_id]['score'] = score
        ranked_list[al_id]['data'] = [name, al_quality, al_follower, twitter, bitly, img]

        # trend
        al_follow_trend = (al_follower - past_data[al_id][0]) / 5
        al_quality_trend = (al_quality - past_data[al_id][1]) /5
        twitter_trend = (twitter - past_data[al_id][2]) / 5
        bitly_trend = (bitly - past_data[al_id][3]) / 5
        trend_list[al_id] = {}
        trend_list[al_id]['score'] = al_follow_trend + al_quality_trend + \
                                     twitter_trend + bitly_trend
        trend_list[al_id]['data'] = [name, al_quality, al_follower, twitter, bitly, img]

    ranked_list = sorted(ranked_list.items(), key=lambda x: x[1]['score'], 
            reverse=True)[0:20]
    trend_list = sorted(trend_list.items(), key=lambda x: x[1]['score'], 
            reverse=True)[0:20]
    
    return render_template("board.html", ranked_list=ranked_list, 
            trend_list=trend_list)

@app.route('/startup')
@app.route('/startup/<int:al_id>')
def startup(al_id):
    al_com = db.session.query(ALCompany).filter(
            ALCompany.angellist_id==al_id).first()

    records = db.session.query(StartupInfo).filter(
            StartupInfo.al_id==al_id).order_by(StartupInfo.info_date).all()

    twitter_data = []
    al_follower_data = []
    al_quality_data = []
    bitly_data = []

    for record in records:
        ts = int(round(float(record.info_date.strftime("%s.%f")), 3)) * 1000
        twitter_data.append([ts, record.twitter_follower])
        al_follower_data.append([ts, record.al_follower])
        al_quality_data.append([ts, record.al_quality])
        bitly_data.append([ts, record.bitly_click])

    data = [
             {"key": "Twitter follower", "values": twitter_data},
             {"key": "Angellist follower", "values": al_follower_data},
             {"key": "Angellist quality", "values": al_quality_data},
             {"key": "Bitly click", "values": bitly_data},
    ];
    
    return render_template("startup.html", data=data, al_com=al_com)
    
@app.route('/predict')
def predict():
    records = db.session.query(al_companies).filter(
            ALCompany.logo_url != None).limit(22)
    #df = pd.read_csv(os.path.join(APP_STATIC, 'predict_com.csv'), header=0, index_col=0)
    #comp_json = json.dumps(["%s (%s)" % (df.ix[cid]['name'], cid) for cid in df.index.values])
    fp = os.path.join(APP_STATIC, 'com.json')
    json_data = open(fp).read()
    comp_json = json.loads(json_data)
    return render_template("predict.html", comp_json=comp_json, records=records)

@app.route('/analyze/', methods=['POST'])
def analyze():
    #records = db.session.query(al_companies).filter(
    #        ALCompany.logo_url != None).limit(22)
    
    fp = os.path.join(APP_STATIC, 'com.json')
    json_data = open(fp).read()
    comp_json = json.loads(json_data)

    crunch_id = request.form.get('crunch-id', None)
    if (crunch_id is None) or (len(crunch_id.strip())==0):
        flash('Please input valid startup name')
        return render_template('predict.html', comp_json=comp_json, records=records)
    
    matobj = re.search("\((.*)\)", crunch_id)
    if matobj:
        crunch_id = matobj.group(1)
    else:
        crunch_id = None
    
    if crunch_id is None:
        flash('Sorry, the input company is not in our database')
        return render_template('predict.html', comp_json=comp_json, records=records)

    model = pickle.load(open(os.path.join(APP_STATIC, 'rf.model')))
    df = pd.read_csv(os.path.join(APP_STATIC, 'predict_com.csv'), header=0, index_col=0)
    del df['name']
    
    row = np.array(df.ix[crunch_id])
    prob = model.predict_proba(row)
    prob = "%.2f%%" % (prob[0][1]*100.0)
    
    record = db.session.query(cb_companies).filter(
            CBCompany.crunch_id==crunch_id).first()
    
    com_record = db.session.query(cb_companies).filter(
            CBCompany.crunch_id==crunch_id).first()
    
    return render_template("analyze.html", prob=prob, \
            company=record, comp_json=comp_json, com_record=com_record)

@app.route('/job')
def job():
    return render_template("job.html")

@app.route('/recommend')
def recommend():
    try:
        token = session['user_oauth_token']
    except KeyError:
        token = None

    if token == None:
        return redirect(url_for('job.login'))

    profile_req_url = 'http://api.linkedin.com/v1/people/~:' + \
        '(id,first-name,last-name,industry,interests,skills,educations,' + \
        'courses,three-current-positions)?format=json'
    resp = linkedin.get(profile_req_url)
    
    if resp.status == 200:
        profile = resp.data

    return render_template('recommend.html', Profile=profile)

@app.route('/login')
def login():
    """
    Calling into authorize will cause the OpenID auth machinery to kick
    in. When all worked out as expected, the remote application will
    redirect back to the callback URL provided.
    """
    return linkedin.authorize(callback=url_for('job.oauth_authorized',
        next=request.args.get('next') or request.referrer or None))

@linkedin.tokengetter
def get_token():
    """This is used by the API to look for the auth token and secret
    it should use for API calls. During the authorization handshake
    a temporary set of token and secret is used, but afterwards this
    function has to return the token and secret. If you don't want
    to store this in the database, consider putting it into the
    session instead.
    """
    try:
        oauth_token = session['user_oauth_token']
        oauth_secret = session['user_oauth_secret']
        if oauth_token and oauth_secret:
            return oauth_token, oauth_secret
    except KeyError:
        pass

@app.route('/oauth_authorized')
@linkedin.authorized_handler
def oauth_authorized(resp, oauth_token=None):
    """
    Called after authorization. After this function finished handling,
    the OAuth information is removed from the session again. When this
    happened, the tokengetter from above is used to retrieve the oauth
    token and secret.
    If the application redirected back after denying, the response passed
    to the function will be `None`. Otherwise a dictionary with the values
    the application submitted. Note that LinkedIn itself does not really
    redirect back unless the user clicks on the application name.
    """
    #next_url = request.args.get('next') or url_for('job.recommend')
    next_url = url_for('job.recommend')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(url_for("job.index"))

    session['user_oauth_token'] = resp['oauth_token']
    session['user_oauth_secret'] = resp['oauth_token_secret']
    
    return redirect(next_url)


if __name__ == "__main__":
    if socket.gethostbyname(socket.gethostname()).startswith('192'):
        port = 5000
    else:
        port = 80

    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)

