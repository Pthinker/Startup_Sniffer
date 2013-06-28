#!/usr/bin/env python

import datetime
import sys
import time
import json
from oauth_hook import OAuthHook
import requests0 as requests
import bitly_api

import config

twitter_oauth_hook = OAuthHook(access_token=config.TWITTER_ACCESS_TOKEN, 
                       access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET, 
                       consumer_key=config.TWITTER_CONSUMER_KEY, 
                       consumer_secret=config.TWITTER_CONSUMER_SECRET, 
                       header_auth=False)

bitly = bitly_api.Connection(access_token=config.BITLY_ACCESS_TOKEN)

class TwitterError(Exception):
    """Base class for Twitter errors
    """
    @property
    def message(self):
        """Returns the first argument used to construct this error.
        """
        return self.args[0]

def throttle_hook(response):
    """ Throttle for twitter API
    """
    ratelimited = "x-rate-limit-remaining" in response.headers and \
                  "x-rate-limit-reset" in response.headers 
    if ratelimited:
        remaining = int(response.headers["x-rate-limit-remaining"])
        reset = datetime.datetime.utcfromtimestamp(float(
            response.headers["x-rate-limit-reset"]))
        now = datetime.datetime.utcnow()
        
        time_to_reset = reset - now
        if remaining == 0:
            time_to_sleep = time_to_reset.seconds
        else:
            time_to_sleep = time_to_reset.seconds / remaining

        sys.stderr.write(
                "Throttling... Sleeping for %d secs...\n" % time_to_sleep)
        time.sleep(time_to_sleep)

def check_twitter_error(data):
    if 'error' in data:
        raise TwitterError(data['error'])
    if 'errors' in data:
        raise TwitterError(data['errors'])

def search_tweets(query=None, count=10, lang='en', result_type='recent'):
    """ Search tweets according to query using twitter API
    """
    client = requests.session(
            hooks={'pre_request': twitter_oauth_hook, 'response': throttle_hook})

    request_url = "https://api.twitter.com/1.1/search/tweets.json?q=%s&lang=%s&count=%d&result_type=%s" % \
                    (query, lang, count, result_type)
    resp = client.get(request_url)
    json_content = resp.content
    try:
        data = json.loads(json_content)
        check_twitter_error(data)
    except ValueError:
        if "<title>Twitter / Over capacity</title>" in json_content:
            raise TwitterError("Capacity Error")
        if "<title>Twitter / Error</title>" in json_content:
            raise TwitterError("Technical Error")
        raise TwitterError("json decoding")

    return data['statuses']

def twitter_user_show(user):
    """ Get user info using twitter API
    """
    client = requests.session(
            hooks={'pre_request': twitter_oauth_hook, 'response': throttle_hook})

    request_url = "https://api.twitter.com/1.1/users/show.json?screen_name=%s" % user
    resp = client.get(request_url)
    json_content = resp.content
    try:
        data = json.loads(json_content)
        check_twitter_error(data)
    except ValueError:
        if "<title>Twitter / Over capacity</title>" in json_content:
            raise TwitterError("Capacity Error")
        if "<title>Twitter / Error</title>" in json_content:
            raise TwitterError("Technical Error")
        raise TwitterError("json decoding")
    return data

def get_bitly_hash(url):
    """Get shorted bitly link from a normal url
    """
    data = None
    while(True):
        try:
            data = bitly.shorten(url)
            break
        except bitly_api.BitlyError as error:
            if str(error) == 'RATE_LIMIT_EXCEEDED':
                print 'Rate limite exceeded, sleeping 1 hr...'
                time.sleep(3601)
                print 'Sleep over, try again...'
            else:
                break

    if data is not None:
        return data['hash']
    else:
        print "Cannot get bitly hash for %s" % url
        return None

def bitly_click_count(bitly_hash):
    """Get bitly url click count
    """
    data = bitly.clicks(hash=bitly_hash)
    return data[0]['global_clicks']

def main():
    #search_tweets("iphone")
    #twitter_user_show("zignallabs")
    
    get_bitly_hash('http://google.com')
    
if __name__ == "__main__":
    main()

