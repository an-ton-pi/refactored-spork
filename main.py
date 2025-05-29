import os
import time
import requests
from flask import Flask
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_IDS = os.getenv("CHAT_IDS", "").split(",")  # можно несколько ID через запятую
INTERVAL = int(os.getenv("INTERVAL", 600))  # по умолчанию 10 минут
BASE_URL = "https://moskvichka.ru"
API_URL = f"{BASE_URL}/api/articles"

sent_article_ids = set()
bot = Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)

def fetch_articles(page=1, limit=10):
    try:
        resp = requests.get(API_URL, params={"page": page, "limit": limit})
        data = resp.json()
        return data.get("items", [])
    except Exception as e:
        print(f"Ошибка при получении статей: {e}")
        return []

def format_article(article):
    url = f"{BASE_URL}/articles/{article['slug']}"
    text = f"📰 <b>{article['title']}</b>\n"
    text += f"🗓 {article['publishDate'][:10]}\n"
    text += f"{article.get('excerpt', '')}\n\n"
    text += f"<a href='{url}'>Читать статью</a>"
    return text

def check_new_articles():
    print("🔎 Проверка сайта на новые статьи...")
    new_articles = []
    articles = fetch_articles(page=1, limit=10)

    for article in articles:
        if article["id"] not in sent_article_ids:
            new_articles.append(article)
            sent_article_ids.add(article["id"])

    print(f"👀 Найдено статей: {len(articles)}")
    print(f"✅ Новых статей отправлено: {len(new_articles)}")

    for article in reversed(new_articles):  # от старых к новым
        text = format_article(article)
        for chat_id in CHAT_IDS:
            try:
                bot.send_message(chat_id=chat_id.strip(), text=text, parse_mode="HTML", disable_web_page_preview=False)
            except Exception as e:
                print(f"Ошибка при отправке статьи в чат {chat_id}: {e}")

@app.route("/")
def index():
    return "Бот работает!", 200

# запуск периодической проверки
def run_scheduler():
    while True:
        check_new_articles()
        time.sleep(INTERVAL)

if __name__ == "__main__":
    from threading import Thread
    Thread(target=run_scheduler, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
