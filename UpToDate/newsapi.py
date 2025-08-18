import requests
from dotenv import load_dotenv
import os
load_dotenv()
API_KEY = os.getenv('API_KEY') ####Replace this line with your actual API key
def get_news():
   # Set up the endpoint and parameters
    url = 'https://newsapi.org/v2/top-headlines'
    params = {
             # You can change to 'de' for Germany, etc.
        'category': 'general',
        'apiKey': API_KEY
    }

    # Make the request
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        articles = data['articles']
        return articles
    #     print("📰 Top Technology Headlines:\n")
    #     for i, article in enumerate(articles[:5], 1):  # show top 5
    #         print(f"{i}. {article['title']}")
    #         print(f"   Source: {article['source']['name']}")
    #         print(f"   URL: {article['url']}\n")
    # else:
    #     print("Failed to fetch news:", response.status_code)

def get_news_category(category:str):
   
    # Set up the endpoint and parameters
    url = 'https://newsapi.org/v2/top-headlines'
    params = {
              # You can change to 'de' for Germany, etc.
        'category': category,
        'apiKey': API_KEY
    }

    # Make the request
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        articles = data['articles']
        return articles

def search_news(word, category):
    url = 'https://newsapi.org/v2/top-headlines'
    params = {
              # You can change to 'de' for Germany, etc.
        'category': category,
        'apiKey': API_KEY,
        'q': word  # Search query
    }

    # Make the request
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        articles = data['articles']
        return articles
    
def clean_headline(headline):
        headline = headline.strip()
        headline = ' '.join([word.strip() for word in headline.split()])
        #  headline = headline.replace(headline[0], '')                                # Replace multiple spaces with a single space
        for x in '$%&123456789':
            headline = headline.removeprefix(x)
            headline = headline.removesuffix(x)

        headline_x = headline.rsplit()
        headline_xx = [wort.capitalize() for wort in headline_x]
        headline = ' '.join(headline_xx)

        return headline