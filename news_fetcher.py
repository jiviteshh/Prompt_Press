import requests
import os
from dotenv import load_dotenv
import cohere

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.Client(COHERE_API_KEY)

def fetch_news_for_topic(topic, lang="en", news_format="full", max_articles=3):
    topic = str(topic).strip()
    if not topic or topic.lower() in ("", "none", "null"):
        return [{
            "title": "Error",
            "description": "❌ No topic provided. Please enter a topic to fetch news.",
            "link": "#",
            "image": None
        }]
    if not NEWS_API_KEY:
        return [{
            "title": "Error",
            "description": "🚫 Missing NEWS_API_KEY in environment.",
            "link": "#",
            "image": None
        }]

    url = "https://newsapi.org/v2/everything"
    params = {
        "apiKey": NEWS_API_KEY,
        "q": topic,
        "language": lang,
        "sortBy": "publishedAt",
        "pageSize": max_articles
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 401:
            return [{
                "title": "Error",
                "description": "🚫 Invalid or expired News API key.",
                "link": "#",
                "image": None
            }]
        elif response.status_code == 429:
            return [{
                "title": "Error",
                "description": "⚠️ API rate limit reached. Try again later.",
                "link": "#",
                "image": None
            }]
        elif response.status_code != 200:
            return [{
                "title": "Error",
                "description": f"⚠️ API error {response.status_code}: {response.text}",
                "link": "#",
                "image": None
            }]
        data = response.json()
        results = data.get("articles", [])
        if not isinstance(results, list) or not results:
            return [{
                "title": "Error",
                "description": f"❌ No news found for topic: {topic}",
                "link": "#",
                "image": None
            }]
        news_items = []
        for article in results[:max_articles]:
            title = article.get("title", "No title")
            link = article.get("url", "#")
            description = article.get("description", "")
            image_url = article.get("urlToImage") or None
            # Summarize if description is missing and format requests a summary
            if news_format == "summary" and not description:
                try:
                    full_text = f"{title}\n{link}"
                    cohere_response = co.summarize(
                        text=full_text,
                        length="medium",
                        format="paragraph",
                        model="command"
                    )
                    description = cohere_response.summary
                except Exception:
                    description = f"⚠️ Could not summarize this article. Title: {title}"

            news_items.append({
                "title": title,
                "link": link,
                "description": description,
                "image": image_url
            })
        return news_items

    except Exception as e:
        return [{
            "title": "Error",
            "description": f"⚠️ Exception occurred while fetching news for '{topic}': {str(e)}",
            "link": "#",
            "image": None
        }]
