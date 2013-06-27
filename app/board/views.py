from flask import Blueprint, render_template, request
from app import db, startup_info, APP_STATIC
from app.models import *
import os
import json
from datetime import datetime

board_page = Blueprint('board', __name__, url_prefix='/board')

@board_page.route('/')
@board_page.route('/index')
def index():
    records = db.session.query(StartupInfo, ALCompany).filter(
            StartupInfo.al_id==ALCompany.angellist_id).filter(
            StartupInfo.info_date==datetime.today().date()).all()
    
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
    
    ranked_list = {}

    for record in records:
        al_follower = record.StartupInfo.al_follower
        al_quality = record.StartupInfo.al_quality
        twitter = record.StartupInfo.twitter_follower
        bitly = record.StartupInfo.bitly_click
        al_id = record.StartupInfo.al_id
        name = record.ALCompany.name
        img = record.ALCompany.logo_url

        nor_al_follower = (al_follower / float(data['angellist'])) * 100.0
        nor_al_quality = al_quality * 10.0
        nor_bitly = (bitly / float(data['bitly'])) * 100.0
        nor_twitter = (twitter / float(data['twitter'])) * 100.0
        
        score = 0.25 * nor_al_follower + 0.25 * nor_al_quality + \
                0.25 * nor_bitly + 0.25 * nor_twitter
        
        ranked_list[al_id] = {}
        ranked_list[al_id]['score'] = score
        ranked_list[al_id]['data'] = [name, al_quality, al_follower, twitter, bitly, img]
    
    ranked_list = sorted(ranked_list.items(), key=lambda x: x[1]['score'], reverse=True)[0:20]
    return render_template("board/index.html", ranked_list=ranked_list)

