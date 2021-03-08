# Script used to automatically collect and downloaded tweets
from scrape import *
import schedule
import time

def schedule_query(hashtags, api, max_interval_query=450):
    """ """
    n_queries = int(max_interval_query/len(hashtags))
    
    print("Waking up to make {0} hashtag queries".format(n_queries))
    df_artem = query_hashtags(hashtags, artem, tweets_per_hashtag=n_queries)
    df_artem["urls"] = df_artem["text"].apply(regex_url)

    print("Saving Artem\n\n")
    df_artem.to_csv(make_df_filename())
    
    print("\n\n----\t----\tSaving images----\t----")
    for url in df_artem["image_urls"]:
        download_image(url)
    print("----------------------------------------"
    print("Downloads complete")


if __name__ == '__main__':
    
    artem = setup_api()
    if artem != -1:
        print("Successfully connected to Twitter!")
    else:
        print("Did not connect to Twitter API")
    artem = setup_api()

    print("Beginning scheduled runs")

    tags = get_hashtags("hashtags.txt")

    n_mins = 1

    schedule_query(tags, artem)
    schedule.every(interval=n_mins).minutes.do( schedule_query, 
                                                hashtags = tags, api = artem)

    while True: 
        # Checks whether a scheduled task  
        # is pending to run or not 
        schedule.run_pending() 
        time.sleep(1) 
    
