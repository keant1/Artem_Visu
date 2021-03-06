import json
from datetime import datetime
import pandas as pd
import numpy as np
import tweepy

# Get API Keys from JSON
def setup_api():
    """Returns authenticated tweepy API object"""
    with open("api_keys.json") as json_file:
        api_keys = json.load(json_file)

    consumer_key = api_keys["API_key"]
    consumer_secret =api_keys["API_secret_key"]

    try: 
        auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)

    except tweepy.TweepError:
        print('Error! Failed to get access token.')
        return -1
    
    return tweepy.API(auth)


def image_query(query):
    return "#{0} -is:retweet filter:images".format(query)


def search_tweets(api, query, n_items=10):
    '''Returns API search for query'''
    results = api.search(query, lang='en', count=n_items)
    return results


def tweet_image_url(tweet):
    """ Returns a list Image URLs in tweets or None, if image url not present"""

    if 'media' in tweet.entities.keys():
      # Filter media for media urls
      image_urls = []
      for i in range(len(tweet.entities["media"])):
          image_urls.append( tweet.entities["media"][i]["media_url"])
    else:
      return None
    
    return image_urls


def tweet_hashtags(tweet):
    """ Returns a list of hashtags in the tweet or None if hashtag not present"""

    if 'hashtags' in tweet.entities.keys():
      # Filter entities for hashtags
      hashtags = []
      for i in range(len(tweet.entities["hashtags"])):
          hashtags.append( tweet.entities["hashtags"][i]["text"])
    else:
      return None


def filter_images(search_results):
    """ Returns list of Image URLs in tweets or None, if image not present"""
    result = []
    for tweet in search_results:
          result.append(tweet_image_url(tweet))
    
    return result

# Iterate through hashtags
def query_hashtags(hashtags, api, tweets_per_hashtag=5):
    """Returns a dataframe of tweets queried in the hashtag"""
    
    df_rows = []
    for tag in hashtags:
        query  = image_query(tag)
        tweets = search_tweets(api, query, n_items=tweets_per_hashtag)

        for tweet in tweets:
            data = {
                'response':  str(tweet._json),
                'text':   tweet.text,
                'main_tag': tag,
                'query':  query,
                'entities': [tweet.entities] if tweet.entities else None,
                'image_urls': tweet_image_url(tweet),
                'hashtags': tweet_hashtags(tweet)
            }
           
            df_rows.append(
                pd.DataFrame(data, columns=data.keys(), index=[0])
            )

    #df_tweets = pd.concat(df_rows, ignore_index=True)

    return pd.concat(df_rows, ignore_index=True)


def make_csv_file():
    try:
        timestamp = datetime.now()
        timestampstr = timestamp.strfrtime("%d-%b-%Y (%H:%M:%S)")

        return " ".join("Artem", datestampstr, ".csv")
    except Exception as e:
        print("Something went wrong!")
        print(e)
        return "Artem.csv"


def get_hashtags():
    pass


if __name__ == '__main__':

    artem = setup_api()

    hashtags = [
        'art','portraits','digitalportrait',
        'illustration','cartoon','sketch','architecture',
        'photography','painting','photography','portrait'
    ]
    
    df_artem = query_hashtags(hashtags, artem, tweets_per_hashtag=1)
    print("Saving Artem CSV")
    df_artem.to_csv(make_csv_file())
