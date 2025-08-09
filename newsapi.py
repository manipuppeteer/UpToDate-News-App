import requests
def get_news():

    API_KEY = 'ecb9e858a7fb47a6aa7b33d668c1ba6e'

    # Set up the endpoint and parameters
    url = 'https://newsapi.org/v2/top-headlines'
    params = {
        'country': 'us',       # You can change to 'de' for Germany, etc.
        'category': 'technology',
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

