import json
import tweepy

# Get API Keys from JSON
def setup_api():
    """Returns authenticated tweepy API object"""
    with open("../api_keys.json") as json_file:
        api_keys = json.load(json_file)

    consumer_key = api_keys["API_key"]
    consumer_secret =api_keys["API_secret_Key"]

    try: 
        auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)

    except tweepy.TweepError:
        print('Error! Failed to get access token.')
        return -1
    
    return tweepy.API(auth)

def search_tweets(api, query, n_items=10):
    result = result
    for tweet in tweepy.Cursor(api.search, q='query').items(n_items):
        result.append(tweet)
        print(tweet.text)
    
    return result


artem = setup_api()
search_tweets(artem, "dog")

# auth = tweepy.OAuthHandler(api_keys["API_key"],
#                            api_keys["API_secret_Key"])
# try:
#     redirect_url = auth.get_authorization_url()
# except tweepy.TweepError:
#     print('Error! Failed to get request token.')

# session.set('request_token', auth.request_token['oauth_token'])



# auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# token = session.get('request_token')
# session.delete('request_token')
# auth.request_token = { 'oauth_token' : token,
#                          'oauth_token_secret' : verifier }

# try:
#     auth.get_access_token(verifier)
# except tweepy.TweepError:
#     print('Error! Failed to get access token.')