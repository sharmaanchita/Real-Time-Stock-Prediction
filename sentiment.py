import requests
from bs4 import BeautifulSoup
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def fetch_headlines(response_text):
    """Extracts headlines from the HTML response."""
    soup = BeautifulSoup(response_text, 'lxml')
    headlines = soup.find_all(attrs={"itemprop": "headline"})
    return [headline.text for headline in headlines]

def get_headers():
    """Returns headers required for making API requests."""
    return {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-IN,en-US;q=0.9,en;q=0.8",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }

def news2sentiment():
    """Fetches news headlines and computes sentiment scores."""
    try:
        # Initialize the Sentiment Analyzer and list to store headlines
        sid_obj = SentimentIntensityAnalyzer()
        news_headlines = []

        # Step 1: Fetch initial headlines
        url = 'https://inshorts.com/en/read'
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP request errors
        news_headlines.extend(fetch_headlines(response.text))

        # Step 2: Fetch more headlines using AJAX
        ajax_url = 'https://inshorts.com/en/ajax/more_news'
        news_offset = "apwuhnrm-1"  # Initial offset (can be dynamic if required)

        for _ in range(3):  # Fetch 3 batches of additional news
            response = requests.post(ajax_url, data={"category": "", "news_offset": news_offset}, headers=get_headers())
            response.raise_for_status()
            response_json = response.json()

            # Extract additional headlines and update the offset
            news_headlines.extend(fetch_headlines(response_json.get("html", "")))
            news_offset = response_json.get("min_news_id", news_offset)  # Use current offset if new one is missing

        # Step 3: Limit and reverse the headlines
        news_headlines = news_headlines[:100][::-1]

        # Step 4: Calculate sentiment scores
        scores = [sid_obj.polarity_scores(headline)['compound'] for headline in news_headlines]

        return scores

    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except json.JSONDecodeError:
        print("Failed to parse JSON from API response.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    # Return an empty list on error
    return []