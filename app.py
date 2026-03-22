from flask import Flask, render_template, request, jsonify
from news_fetcher import fetch_news_for_topic
from email_utils import send_news_email
from newspaper import Article
from groq import Groq
import cohere
import os
import re
from dotenv import load_dotenv
from weather_utils import get_weather, get_weather_nlg
from stock_utils import get_stock, get_stock_nlg


load_dotenv()

app = Flask(__name__)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

if not NEWS_API_KEY or not COHERE_API_KEY or not GROQ_API_KEY:
    raise ValueError("🚫 Missing API keys in .env file")

co = cohere.Client(COHERE_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

# Active Groq model IDs verified against Groq docs on 2026-03-22.
PRIMARY_GROQ_CHAT_MODEL = "llama-3.3-70b-versatile"
GROQ_INSIGHT_MODELS = [
    PRIMARY_GROQ_CHAT_MODEL,
    "qwen/qwen3-32b",
    "llama-3.1-8b-instant",
]

# ---------------------------------------------------------------------------
# Related-news helper — pure Python, no extra dependencies
# ---------------------------------------------------------------------------
_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "has", "have", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "this", "that", "it", "its", "as",
    "up", "out", "about", "into", "than", "more", "after", "over", "also",
}

def _title_keywords(title: str) -> set:
    """Return meaningful lowercase words from a title."""
    words = re.findall(r"[a-zA-Z]+", (title or "").lower())
    return {w for w in words if len(w) > 2 and w not in _STOPWORDS}

def get_related_articles(current_article, all_articles, top_n=3):
    """
    Return up to `top_n` articles from `all_articles` that share the most
    title keywords with `current_article`. The current article itself is
    excluded. Articles with zero overlap are not returned.
    """
    current_link = current_article.get("link", "")
    current_kw = _title_keywords(current_article.get("title", ""))
    if not current_kw:
        return []

    scored = []
    for art in all_articles:
        if art.get("link", "") == current_link:
            continue
        score = len(current_kw & _title_keywords(art.get("title", "")))
        if score > 0:
            scored.append((score, art))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [art for _, art in scored[:top_n]]


@app.route("/", methods=["GET"])
@app.route("/dashboard", methods=["GET"])
def dashboard():
    topic = request.args.get("topic")
    lang = request.args.get("lang", "en")
    if topic:
        topic_news_raw = fetch_news_for_topic(topic, lang)
        # Attach related articles
        for art in topic_news_raw:
            art["related"] = get_related_articles(art, topic_news_raw)
        return render_template(
            "dashboard.html",
            current_topic=topic,
            lang=lang,
            topic_news={topic: topic_news_raw},
            top_news=None,
            breaking_news=None,
            trending_news=None
        )
    else:
        top_news = fetch_news_for_topic("Top News", lang)
        breaking_news = fetch_news_for_topic("Breaking News", lang)
        trending_topics = ["AI", "Technology", "Finance"]
        trending_news = {t: fetch_news_for_topic(t, lang) for t in trending_topics}

        # Build one flat pool per section for cross-article similarity
        all_top = top_news + breaking_news
        for art in top_news:
            art["related"] = get_related_articles(art, all_top)
        for art in breaking_news:
            art["related"] = get_related_articles(art, all_top)
        for topic_key, arts in trending_news.items():
            for art in arts:
                art["related"] = get_related_articles(art, arts)

        return render_template(
            "dashboard.html",
            current_topic=None,
            lang=lang,
            topic_news=None,
            top_news=top_news,
            breaking_news=breaking_news,
            trending_news=trending_news
        )


@app.route("/mail_news", methods=["POST"])
def mail_news():
    email = request.form.get("email", "").strip()
    title = request.form.get("title", "").strip()
    link = request.form.get("link", "").strip()
    desc = request.form.get("desc", "").strip()
    image = request.form.get("image", "").strip()

    if not email or "@" not in email:
        return jsonify({"success": False, "error": "Valid email is required."}), 400

    if not title:
        return jsonify({"success": False, "error": "Article missing."}), 400

    try:
        article = {
            "title": title,
            "description": desc,
            "link": link,
            "image": image
        }
        send_news_email(email, {"Selected Article": [article]})
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to send email: {str(e)}"}), 500

    return jsonify({"success": True})

@app.route("/summarize_api", methods=["POST"])
def summarize_api():
    data = request.get_json()
    link = data.get("link", "")
    try:
        article = Article(link)
        article.download()
        article.parse()
        full_text = article.text

        if len(full_text.strip()) < 250:
            return jsonify({"summary": "⚠️ Article content is too short to summarize."})
        
        prompt = f"Summarize the following article in a medium-length paragraph:\n\n{full_text}"
        response = co.chat(message=prompt)
        return jsonify({"summary": response.text})

    except Exception as e:
        return jsonify({"summary": f"⚠️ Failed to summarize: {str(e)}"})

@app.route("/chatbot_api", methods=["POST"])
def chatbot_api():
    data = request.get_json()
    # Support both "message" (new) and "question" (legacy) keys
    user_input = (data.get("message") or data.get("question") or "").strip()
    article_context = (data.get("context") or "").strip()

    if not user_input:
        return jsonify({"answer": "⚠️ Please enter a message."})

    # Handle greetings
    if user_input.lower() in ["hi", "hello", "hey"]:
        return jsonify({"answer": "👋 Welcome to PromptPress! Ask me about the article..."})

    # Build messages depending on whether an article context is provided
    if article_context:
        system_prompt = (
            "You are a helpful news assistant on PromptPress. "
            "Answer questions ONLY based on the article provided by the user. "
            "Keep your answer short and clear (2-3 lines). "
            "If the answer is not present in the article, respond with exactly: "
            "'This information is not available in the article.'"
        )
        user_prompt = (
            f"Answer the question strictly based on the following article.\n"
            f"If the answer is not present in the article, say:\n"
            f"'This information is not available in the article.'\n\n"
            f"Article:\n{article_context}\n\n"
            f"Question:\n{user_input}"
        )
    else:
        # Fallback: general-purpose chatbot (no article selected)
        system_prompt = (
            "You are a helpful chatbot on a news dashboard called PromptPress. "
            "Format your answers neatly. Use short paragraphs, bullet points when listing, "
            "and keep everything visually clean and easy to read. Avoid massive blocks of text."
        )
        user_prompt = user_input

    try:
        response = groq_client.chat.completions.create(
            model=PRIMARY_GROQ_CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return jsonify({"answer": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"answer": f"⚠️ Error: {str(e)}"}), 500
    

@app.route('/api/weather', methods=['GET'])
def api_weather():
    city = request.args.get('city', 'New York')
    weather = get_weather(city)
    if not weather:
        return jsonify({"error": "City not found"}), 404

    # Build LLM-powered insight using the requested prompt
    weather_prompt = (
        f"You are an assistant that explains weather in a simple and useful way.\n\n"
        f"Given the weather data below, generate a short insight (2–3 lines) that explains:\n"
        f"- How the weather feels\n"
        f"- Any impact on daily activities (travel, outdoor work, comfort)\n\n"
        f"Keep it simple and practical.\n\n"
        f"Weather Data:\n"
        f"- Temperature: {weather['temp']}°C\n"
        f"- Condition: {weather['condition']}\n"
        f"- Humidity: {weather['humidity']}%\n"
        f"- Wind Speed: {weather['wind']} m/s"
    )
    try:
        llm_response = groq_client.chat.completions.create(
            model=PRIMARY_GROQ_CHAT_MODEL,
            messages=[{"role": "user", "content": weather_prompt}]
        )
        summary = llm_response.choices[0].message.content.strip()
    except Exception:
        # Fallback to simple summary if LLM is unavailable
        summary = get_weather_nlg(weather)

    return jsonify({**weather, "summary": summary})

@app.route('/api/stock', methods=['GET'])
def api_stock():
    symbol = request.args.get('symbol', 'AAPL')
    stock = get_stock(symbol)
    if not stock:
        return jsonify({"error": "Symbol not found"}), 404

    # Build LLM-powered insight using the requested prompt
    stock_prompt = (
        f"Keep the tone neutral and informative. Do not exaggerate.\n"
        f"You are a financial assistant that explains stock movement in simple terms.\n\n"
        f"Given the stock data below, generate a short insight (2–3 lines) that explains:\n"
        f"- Whether the stock is rising, falling, or stable\n"
        f"- What this might indicate about market sentiment\n\n"
        f"Do NOT give financial advice. Keep it neutral and easy to understand.\n\n"
        f"Stock Data:\n"
        f"- Symbol: {stock['symbol']}\n"
        f"- Price: ${stock['price']:.2f}\n"
        f"- Change: {stock['change']:+.2f}\n"
        f"- Percentage Change: {stock['pct']:+.2f}%"
    )
    try:
        llm_response = groq_client.chat.completions.create(
            model=PRIMARY_GROQ_CHAT_MODEL,
            messages=[{"role": "user", "content": stock_prompt}]
        )
        summary = llm_response.choices[0].message.content.strip()
    except Exception:
        # Fallback to simple summary if LLM is unavailable
        summary = get_stock_nlg(stock)

    return jsonify({**stock, "summary": summary})


@app.route('/insight', methods=['POST'])
def insight():
    """Generate insight for article text using Groq LLM"""
    data = request.get_json()
    text = data.get("text", "").strip()
    
    if not text:
        return jsonify({"insight": "⚠️ No text provided."})
    
    for model in GROQ_INSIGHT_MODELS:
        try:
            response = groq_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a news analyst. Generate a brief 2-3 line insight about news articles covering: 1) Why this news is important, 2) Who it impacts, 3) What could happen next (optional). Keep it concise and clear."
                    },
                    {
                        "role": "user",
                        "content": f"Generate an insight for this news: {text}"
                    }
                ]
            )
            
            insight_text = response.choices[0].message.content.strip()
            return jsonify({"insight": insight_text})
        
        except Exception as e:
            error_msg = str(e)
            # Skip invalid or retired model IDs and try the next fallback.
            if (
                "decommissioned" in error_msg.lower()
                or "model_decommissioned" in error_msg.lower()
                or "model_not_found" in error_msg.lower()
            ):
                continue
            # Otherwise return the error
            return jsonify({"insight": f"⚠️ Failed to generate insight: {error_msg}"})
    
    # If all models fail
    return jsonify({"insight": "⚠️ All available models are currently unavailable. Please try again later."})


if __name__ == "__main__":
    app.run(debug=True)
