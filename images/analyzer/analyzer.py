import os, logging
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

def get_top_5_liked_tweets_containing_text(df, text):
    """
    Retrieves the top 5 most liked tweets that contain the specified text.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing tweet data.
    - text (str): Text to search for within tweet contents.

    Returns:
    - dict: A dictionary containing the title based on the search results and 
            the top 5 most liked tweets as a list of dictionaries.
    """
    # Ensure the search text is in lower case for case-insensitive matching
    search_text = text.lower()
    
    # Filter tweets that contain the specified text
    matching_tweets = df[df['content'].str.lower().str.contains(search_text)]
    
    # Sort the filtered tweets by number of likes in descending order
    sorted_tweets = matching_tweets.sort_values(by='likes', ascending=False)
    
    # Select the top 5 most liked tweets and specific columns
    top_5_tweets = sorted_tweets.head(5)[["content", "author", "likes"]]
    top_5_tweets_list = top_5_tweets.to_dict(orient='records')
    
    # Determine the title based on the number of tweets found
    num_tweets_found = len(top_5_tweets_list)
    if num_tweets_found == 0:
        title = "No tweets found"
    else:
        title = f"Top {min(num_tweets_found, 5)} most liked tweets containing '{search_text}'"
    
    return {
        "type": "dict",
        "title": title,
        "data": top_5_tweets_list
    }

def count_tweets_containing_text_by_year(df, text):
    """
    Counts how many times a specified text appears in tweets by year, plots the results, 
    and saves the plot to an image file.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing tweet data with 'content' and 'timestamp' columns.
    - text (str): Text to search for within the tweets' content.

    Returns:
    - dict: Information about the generated image including type, title, and file path.
    """
    # Ensure case-insensitive search
    lower_search_text = text.lower()

    # Prepare image file path and name
    image_name = 'tweets_by_year.png'
    image_path = os.path.join(os.getenv('ANALYZER_IMAGE_PATH'), image_name)

    try:
        # Filter tweets containing the specified text and extract year from timestamp
        df['year'] = pd.to_datetime(df['timestamp'], format='%d/%m/%Y %H:%M').dt.year
        matching_tweets_by_year = (
            df[df['content'].str.lower().str.contains(lower_search_text, na=False)]
            .groupby('year')
            .size()
            .reset_index(name='count')
        )

        # Plotting
        plt.figure(figsize=(10, 6))
        plt.bar(matching_tweets_by_year['year'], matching_tweets_by_year['count'], color='skyblue')
        plt.xlabel('Year', fontsize=14)
        plt.ylabel('Number of Tweets', fontsize=14)
        plt.title(f'Number of Tweets Containing "{text}" by Year', fontsize=16)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)

        # Save the plot
        plt.savefig(image_path)
        plt.close()

        return {
            "type": "image",
            "title": f'Number of Tweets Containing "{text}" by Year',
            "name": image_name
        }
    
    except Exception as e:
        logging.warning(f"An error occurred: {e}")
        return {}

def plot_authors_tweet(df, text):
    """
    Plots the number of tweets containing a specified text by each author and saves the plot as an image.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing tweet data.
    - text (str): Text to search for within tweet contents.

    Returns:
    - dict: A dictionary with details about the generated image.
    """
    text_og = text
    text = text.lower()
    
    image_name = 'count_authors.png'
    image_path = os.path.join(os.getenv('ANALYZER_IMAGE_PATH'), image_name)

    # Filter tweets that contain the specified text
    matching_tweets = df[df['content'].str.lower().str.contains(text)]
    
    # Count the number of authors that have tweeted the specified text
    matching_tweets_by_author = matching_tweets.groupby('author').size()
    matching_tweets_by_author = matching_tweets_by_author.reset_index(name='count')
    matching_tweets_by_author = matching_tweets_by_author.sort_values(by='count', ascending=False)
    
    # Plot the number of authors that have tweeted the specified text
    plt.bar(matching_tweets_by_author['author'].head(10), matching_tweets_by_author['count'].head(10))
    plt.xlabel('Author')
    plt.ylabel('Number of tweets')
    plt.title('Number of tweets that contain the text: ' + text_og + ' by author')
    plt.xticks(rotation=45, ha='right')  # Rotate the x-labels by 45 degrees and align them to the right
    plt.tight_layout()  # Adjust layout to prevent overlap

    plt.savefig(image_path)
    plt.close()

    return {
        "type": "image",
        "title": "Number of tweets by author",
        "name": image_name
    }

def engagement_for_the_text(df, text):
    """
    Generates a plot showing the total number of likes and retweets (shares) for tweets containing
    a specified text, aggregated over the years, and saves it as an image.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing tweet data with 'content', 'timestamp', 'likes', and 'shares'.
    - text (str): Text to search for within the tweet contents.

    Returns:
    - dict: A dictionary with details about the generated image.
    """
    image_name = 'engagement.png'
    image_path = os.path.join(os.getenv('ANALYZER_IMAGE_PATH'), image_name)

    # polt the number of likes, retweets for the specified text over the years
    text_og = text
    text = text.lower()
    matching_tweets = df[df['content'].str.lower().str.contains(text)]
    matching_tweets['year'] = pd.to_datetime(matching_tweets['timestamp'], format='%d/%m/%Y %H:%M').dt.year
    matching_tweets_by_year = matching_tweets.groupby('year').agg({'likes': 'sum', 'shares': 'sum'}).reset_index()
    plt.plot(matching_tweets_by_year['year'], matching_tweets_by_year['likes'], label='Likes')
    plt.plot(matching_tweets_by_year['year'], matching_tweets_by_year['shares'], label='Retweets')
    plt.xlabel('Year')
    plt.ylabel('Engagement')
    plt.title('Engagement for the text: ' + text_og + ' over the years')
    plt.legend()
    plt.savefig(image_path)
    plt.close()

    return {
        "type": "image",
        "title": "Engagement over the years",
        "name": image_name
    }

def word_cloud(df, text):
    """
    Generates a word cloud image from tweets containing a specified text, after excluding the search text itself,
    and saves the image to a specified path.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing tweet data with a 'content' column.
    - text (str): Text to search for within the tweet contents.

    Returns:
    - dict: A dictionary with details about the generated image.
    """
    image_name = 'wordcloud.png'
    image_path = os.path.join(os.getenv('ANALYZER_IMAGE_PATH'), image_name)

    text = text.lower()
    matching_tweets = df[df['content'].str.lower().str.contains(text)]
    #remove text from tweets
    case_insensitive_regex = rf'(?i){text}'  # (?i) makes the regex match case insensitive
    matching_tweets['content'] = matching_tweets['content'].str.replace(case_insensitive_regex, '', regex=True)
    
    words_count = {}
    for tweet in matching_tweets['content']:
        for word in tweet.split():
            if word in words_count:
                words_count[word] += 1
            else:
                words_count[word] = 1

    #sort the dictionary
    words_count = dict(sorted(words_count.items(), key=lambda item: item[1], reverse=True))
    #remove words with less than 3 characters
    words_count = {key:val for key, val in words_count.items() if len(key) > 3}
    #keep the top 10 words      
    words_count = dict(list(words_count.items())[:10])

    wordcloud = WordCloud(width = 800, height = 800,
                background_color ='white',
                stopwords = set(STOPWORDS),
                min_font_size = 10).generate_from_frequencies(words_count)
    plt.figure(figsize = (8, 8), facecolor = None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad = 0)
    plt.savefig(image_path)
    plt.close()

    return {
        "type": "image",
        "title": "Word Cloud",
        "name": image_name
    }

def top_5_languages(df, text):
    """
    Identifies the top 5 languages with the most tweets containing a specified text.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing tweet data.
    - text (str): Text to search for within tweet content.

    Returns:
    - dict: A dictionary containing information about the top 5 languages by tweet count.
    """
    # Normalize search text to lower case for case-insensitive matching
    text = text.lower()

    # Filter tweets containing the text and count occurrences by language
    matching_tweets_by_language = (
        df[df['content'].str.lower().str.contains(text)]  # Filter matching tweets
        .groupby('language')  # Group by language
        .size()  # Count tweets per language
        .reset_index(name='count')  # Convert to DataFrame
        .sort_values(by='count', ascending=False)  # Sort by count
        .head(5)  # Limit to top 5
        .to_dict(orient='records')  # Convert to list of dicts
    )

    # Prepare and return the result
    return {
        "type": "dict",
        "title": "Top languages with the most tweets",
        "data": matching_tweets_by_language
    }


def analyze(text, data):
    df = pd.DataFrame(data)
    insights = [get_top_5_liked_tweets_containing_text, 
                count_tweets_containing_text_by_year, 
                plot_authors_tweet,
                engagement_for_the_text,
                word_cloud, 
                top_5_languages]
    
    return [insight(df, text) for insight in insights]


    
    
    


    

