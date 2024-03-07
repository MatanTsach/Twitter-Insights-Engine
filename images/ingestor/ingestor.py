import os, requests, logging, json
import pandas as pd

def ingest_csv(keyword, redis_key, redis_client):
    logging.info('Starting to ingest CSV')

    # Read the CSV file
    df = pd.read_csv('tweets.csv')

    # Filter relevant tweets
    df = df[df['content'].str.contains(keyword, case=False)]

    # Store the filtered tweets in Redis
    for _, row in df.iterrows():
        tweet_data = json.dumps({
            'content': row['content'],
            'author': row['author'],
            'timestamp': row['date_time'],
            'likes': row['number_of_likes'],
            'shares': row['number_of_shares'],
            'language': row['language']
        })

        redis_client.rpush(redis_key, tweet_data)

def ingest_api(keyword, redis_key, redis_client):
    # Prepare the API request header
    headers = {
        "Authorization": f"Bearer {os.getenv('TWITTER_BEARER_TOKEN')}"
    }

    # Twitter API endpoint for searching tweets
    search_url = "https://api.twitter.com/2/tweets/search/recent"

    query_params = {
        'query': keyword + " -is:retweet",  # Exclude retweets
        'tweet.fields': 'created_at,public_metrics',  # Request additional fields
    }

    try:
        # Make the request to the Twitter API
        response = requests.get(search_url, headers=headers, params=query_params)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the JSON response
        tweets_data = response.json()
        tweets = tweets_data['data']

        for tweet in tweets:
            tweet_data = json.dumps({
                'content': tweet['text'],
                'author': tweet['author_id'],  # You might need an additional call to resolve usernames from IDs
                'timestamp': tweet['created_at'],
                'likes': tweet['public_metrics']['like_count'],
                'shares': tweet['public_metrics']['retweet_count'],
                'language': tweet['lang']
            })

            redis_client.rpush(redis_key, tweet_data)

    except Exception as e:
        print(f"Error fetching tweets: {e}")
        return []