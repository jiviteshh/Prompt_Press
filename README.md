# 📰 PromptPress — AI News Dashboard

> A full-stack AI-powered news dashboard that transforms how you experience news — with live aggregation, smart summaries, automated newsletters, and an AI copilot, all in one place.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Video_Demo-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/posts/naragam-jivitesh-71a4b8313_ai-python-flask-activity-7352672507297976322-vEnx)
[![GitHub](https://img.shields.io/badge/GitHub-jiviteshh-181717?style=for-the-badge&logo=github)](https://github.com/jiviteshh)
[![Built With Flask](https://img.shields.io/badge/Built%20With-Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![AI Powered](https://img.shields.io/badge/AI-Powered-8A2BE2?style=for-the-badge&logo=openai&logoColor=white)]()
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

---

## 📽️ Demo

> 🎬 **Watch the full walkthrough on LinkedIn:** [Click here to view the screen recording](https://www.linkedin.com/posts/naragam-jivitesh-71a4b8313_ai-python-flask-activity-7352672507297976322-vEnx)

---

## 📌 Overview

**PromptPress** is a full-stack AI news dashboard that brings together live news, AI summaries, personalized newsletters, weather, stocks, and a conversational copilot — all inside a single modern interface. Built with Flask and powered by multiple real-world APIs, it's designed to cut through information overload and deliver exactly what matters, instantly.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📰 **Live News Aggregator** | Real-time topic search, trending headlines, and daily news digests |
| 📩 **Mail My News** | AI-personalized newsletters auto-delivered every morning via Gmail SMTP |
| 🧠 **AI Summaries** | One-tap smart summaries powered by Cohere to cut through the clutter |
| 🤖 **Copilot Chatbot** | Floating AI sidebar for news Q&A, weather queries, and general conversation via Groq |
| 🌦️ **Weather Widget** | Real-time weather updates with AI-generated daily summaries |
| 📈 **Stocks Widget** | Live stock data with AI-powered market insights |
| 🎨 **Modern UI** | Mobile-first design with animated modals, popups, and a floating chat sidebar |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask (Python), Jinja2 Templates |
| Frontend | Vanilla JavaScript, Modular HTML/CSS |
| Email Automation | Gmail SMTP |
| News API | Newsdata.io |
| Weather API | OpenWeatherMap |
| Stocks API | Alpha Vantage |
| AI Summarization | Cohere API |
| AI Chatbot | Groq |

---

## 🔌 API Keys Required

Create a `.env` file in the root directory:

```env
NEWS_API_KEY=your_newsdata_io_key
WEATHER_API_KEY=your_openweathermap_key
STOCKS_API_KEY=your_alpha_vantage_key
COHERE_API_KEY=your_cohere_key
GROQ_API_KEY=your_groq_key
GMAIL_USER=your_gmail_address
GMAIL_PASSWORD=your_gmail_app_password
```

---

## 🚀 Getting Started

### Prerequisites

- Python `3.10+`
- pip
- Gmail account with App Password enabled

### Installation

```bash
# Clone the repository
git clone https://github.com/jiviteshh/promptpress.git

# Navigate into the project
cd promptpress

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add your API keys to .env file

# Start the development server
python app.py
```

Then open your browser and visit: `http://127.0.0.1:5000`

---

## 🔄 How It Works

```
User opens PromptPress Dashboard
        ↓
Live news fetched from Newsdata.io in real time
        ↓
User taps summary → Cohere API returns AI summary instantly
        ↓
Copilot sidebar → Groq handles Q&A and general chat
        ↓
Weather & Stocks widgets → live data + AI daily insights
        ↓
Every morning → Gmail SMTP delivers personalized AI newsletter
```

---

## 🗺️ Roadmap

- [ ] User authentication & saved preferences
- [ ] Category-based news filtering (Tech, Sports, Finance, etc.)
- [ ] Bookmark and read-later functionality
- [ ] Multi-language news support
- [ ] Deployed live version

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Jivitesh**  
Built to explore the intersection of AI, APIs, and full-stack web development. 🧠📰

- GitHub: [@jiviteshh](https://github.com/jiviteshh)
- LinkedIn: [linkedin.com/in/naragam-jivitesh-71a4b8313](https://www.linkedin.com/in/naragam-jivitesh-71a4b8313)

---

> 💡 *Want to try it out, collaborate, or give feedback? Reach out on LinkedIn — always open to connecting!*

> ⭐ If you found this project interesting, please give it a star!
