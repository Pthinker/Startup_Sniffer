#!/usr/bin/env python

import datetime
import sys
import time
import json
from oauth_hook import OAuthHook
import requests0 as requests

import config


twitter_oauth_hook = OAuthHook(access_token=config.TWITTER_ACCESS_TOKEN, 
                       access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET, 
                       consumer_key=config.TWITTER_CONSUMER_KEY, 
                       consumer_secret=config.TWITTER_CONSUMER_SECRET, 
                       header_auth=False)

def throttle_hook(response):
    ratelimited = "x-ratelimit-remaining" in response.headers and \
                  "x-ratelimit-reset" in response.headers 

    if ratelimited:
        remaining = int(response.headers["x-ratelimit-remaining"])
        reset = datetime.datetime.utcfromtimestamp(float(response.headers["x-ratelimit-reset"]))
        now = datetime.datetime.utcnow()
        
        time_to_reset = reset - now
        time_to_sleep = time_to_reset.seconds / remaining

        sys.stderr.write("Throttling... Sleeping for %d secs...\n" % time_to_sleep)
        time.sleep(time_to_sleep)

class TwitterError(Exception):
    """Base class for Twitter errors
    """
    @property
    def message(self):
        """Returns the first argument used to construct this error.
        """
        return self.args[0]

def check_twitter_error(data):
    if 'error' in data:
        raise TwitterError(data['error'])
    if 'errors' in data:
        raise TwitterError(data['errors'])

def search_tweets(query=None, count=10, lang='en', result_type='recent'):
    client = requests.session(hooks={'pre_request': twitter_oauth_hook, 'response': throttle_hook})

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

    # parse json data
    for tweet in data['statuses']:
        print tweet["text"]

def main():
    search_tweets("iphone")

if __name__ == "__main__":
    main()

