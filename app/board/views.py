from flask import Blueprint, render_template, request
from app import db, startup_info, APP_STATIC
from app.models import *
import os
import json

board_page = Blueprint('board', __name__, url_prefix='/board')

@board_page.route('/')
@board_page.route('/index')
def index():
    records = db.session.query(StartupInfo, ALCompany).filter(
            StartupInfo.al_id==ALCompany.angellist_id).limit(20).all()
    return render_template("board/index.html", records=records)
