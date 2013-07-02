from flask import Blueprint, render_template, request, jsonify
from app import db, startup_info, APP_STATIC
from app.models import *
import os
import json
from datetime import date, timedelta, datetime
import json

board_page = Blueprint('board', __name__, url_prefix='/board')

@board_page.route('/')
@board_page.route('/index')
def index():
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
    
    return render_template("board/index.html", ranked_list=ranked_list, 
            trend_list=trend_list)

@board_page.route('/startup')
@board_page.route('/startup/<int:al_id>')
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
        ts = int(record.info_date.strftime("%s")) * 1000
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
    
    return render_template("board/startup.html", data=data, al_com=al_com)
    
