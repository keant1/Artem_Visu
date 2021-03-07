import json
from datetime import datetime
import pandas as pd
import re
import tweepy

import tempfile
import requests
import shutil

with open("api_keys.json") as json_file:
    api_keys = json.load(json_file)

# Get API Keys from JSON
def setup_api():
    """Returns authenticated tweepy API object"""

    consumer_key = api_keys["API_key"]
    consumer_secret = api_keys["API_secret_key"]

    try: 
        auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)

    except tweepy.TweepError:
        print('Error! Failed to get access token.')
        return -1
    
    return tweepy.API(auth)


def image_query(query):
    return "#{0} filter:twimg -filter:retweets -filter:replies".format(query)

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
    # TKE DELETE: Unused function
    """ Returns list of Image URLs in tweets or None, if image not present"""
    result = []
    for tweet in search_results:
          result.append(tweet_image_url(tweet))
    
    return result


def regex_url(tweet_text):
    """ Returns a list of all the URLs in """
    pattern = r'(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}[-a-zA-Z0-9()@:%_+.~#?&/=]*)'
    return re.findall(pattern, tweet_text)
    

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


def make_df_filename(use_csv=True):
    if use_csv==True:
        end = ".csv"
    elif type(use_csv) == str:
        end = use_csv
    else:
        end = ".xlsx"

    try:
        timestamp = datetime.now()
        timestampstr = timestamp.strftime("%d-%b-%Y (%H:%M:%S)")

        return "runs/Artem " + timestampstr + end
    except Exception as e:
        print("Something went wrong!")
        print(e)
        return "runs/Artem " + end 


def download_image(url):
    """Downloads images from media urls"""

    if url == 'nan':
        return None
    
    try:
        response = requests.get(url)

        temp_name = next(tempfile._get_candidate_names())
        header = 'Authorization: Bearer ' + api_keys["Bearer_Token"] 
        response = requests.get(url)

        if response.status_code == 200:
            print(url)
            img = open("images/" + temp_name + ".jpg", "xb")
            img.write(response.content)
            img.close()
    
    except:
        pass


if __name__ == '__main__':

    artem = setup_api()
    if artem != -1:
        print("Successfully connected to Twitter!")
    else:
        print("Did not connect to Twitter API")

    hashtags = [
        'art','portraits','digitalportrait',
        'illustration','cartoon','sketch','architecture',
        'photography','painting','portrait', 
    ]

    
    df_artem = query_hashtags(hashtags, artem, tweets_per_hashtag=10)
    df_artem["urls"] = df_artem["text"].apply(regex_url)

    print("Saving Artem")
    df_artem.to_csv(make_df_filename())
    
    print("Saving images")
    for url in df_artem["image_urls"]:
        download_image(url)
    
