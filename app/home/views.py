from flask import Blueprint, render_template
from app import db, cb_companies
from app.models import *

mod = Blueprint('home', __name__, url_prefix='/home')

@mod.route('/index/')
def index():
    #records = db.session.query(cb_companies).filter(CBCompany.category=='mobile').all()
    return render_template("home/index.html")
