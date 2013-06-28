from flask import Blueprint, render_template, request
from app import db, startup_info, APP_STATIC
from app.models import *
import os
import json
from datetime import date, timedelta

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
            StartupInfo.info_date==(date.today()-timedelta(3))).all()

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
        al_follow_trend = (al_follower - past_data[al_id][0]) / 3
        al_quality_trend = (al_quality - past_data[al_id][1]) /3
        twitter_trend = (twitter - past_data[al_id][2]) / 3
        bitly_trend = (bitly - past_data[al_id][3]) / 3
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

