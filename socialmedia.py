import twitter

import config


twitter_api = twitter.Api(consumer_key = config.TWITTER_CONSUMER_KEY, 
                          consumer_secret = config.TWITTER_CONSUMER_SECRET, 
                          access_token_key = config.TWITTER_ACCESS_TOKEN, 
                          access_token_secret = config.TWITTER_ACCESS_TOKEN_SECRET)

def twitter_search(query="twitter"):
    tweets = twitter_api.GetSearch(query, count=100, lang='en')
    for tweet in tweets:
        print tweet.text

def twitter_user(query="facebook"):
    """bulk user query, users/lookup
    """
    pass

def main():
    twitter_search("iphone")

if __name__ == "__main__":
    main()
