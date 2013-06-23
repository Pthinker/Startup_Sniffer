from flask import Blueprint, render_template, request
from flask import redirect, url_for, session, flash
from flask_oauth import OAuth

from app import *

oauth = OAuth()


job_page = Blueprint('job', __name__, url_prefix='/job')

linkedin = oauth.remote_app(
    base_url = 'http://api.linkedin.com/v1/',
    name = 'linkedin',
    consumer_key = app.config['LINKEDIN_API_KEY'],
    consumer_secret = app.config['LINKEDIN_SECRET_KEY'],
    request_token_url = 'https://api.linkedin.com/uas/oauth/requestToken?scope=r_fullprofile',
    access_token_url = 'https://api.linkedin.com/uas/oauth/accessToken',
    authorize_url = 'https://www.linkedin.com/uas/oauth/authenticate')

@job_page.route('/')
@job_page.route('/index')
def index():
    return render_template("job/index.html")

@job_page.route('/recommend')
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

    return render_template('job/recommend.html', Profile=profile)

@job_page.route('/login')
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

@job_page.route('/oauth_authorized')
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

