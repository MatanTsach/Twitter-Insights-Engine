import requests

bearer_token = 'AAAAAAAAAAAAAAAAAAAAAJOTsgEAAAAA9p5wGcM9gE2tdB4pa8%2BzyVXc43w%3D1w0NBorvHefSL0f0WEdjemCnByjBdTVV7sDheqGeCVBNwlcxYy'  # Replace YOUR_BEARER_TOKEN_HERE with your actual bearer token

def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

def create_url(keyword, start_time, end_time):
    search_url = "https://api.twitter.com/2/tweets/search/recent"  # Endpoint for recent search

    # change params based on the needs of your search
    query_params = {
        'query': keyword,  # Your search query
        'start_time': start_time,  # Start time for the search window
        'end_time': end_time,  # End time for the search window
        'max_results': 10,  # Adjust the number of results as needed
        'tweet.fields': 'author_id,created_at,lang'  # Example of specifying which tweet fields you want
    }
    return search_url, query_params

def connect_to_endpoint(url, headers, params):
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

# Import Python's datetime module to calculate the start and end times
from datetime import datetime, timedelta

# Calculate start and end times for the last 7 days
end_time = datetime.now()
start_time = end_time - timedelta(days=7)

# Convert times to ISO format for the API request
start_time = start_time.isoformat("T") + "Z"
end_time = end_time.isoformat("T") + "Z"

# Setup the request
keyword = "Israel"
url, query_params = create_url(keyword, start_time, end_time)
headers = create_headers(bearer_token)

# Make the request
json_response = connect_to_endpoint(url, headers, query_params)
print(json_response)
