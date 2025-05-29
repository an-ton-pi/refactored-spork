import json
import os
import time
import threading
from flask import Flask
import requests
from telegram import Bot

# Telegram
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
CHAT_IDS = os.getenv("CHAT_IDS", "").split(",")  # через запятую
bot = Bot(token=TELEGRAM_TOKEN)

# Статьи
SENT_FILE = "sent_articles.json"
API_URL = "https://moskvichka.ru/api/articles?page=1&limit=10"


def load_sent_articles():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_sent_articles(sent_ids):
    with open(SENT_FILE, "w") as f:
        json.dump(list(sent_ids), f)


def fetch_articles(page=1, limit=10):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; TelegramBot/1.0)",
            "Accept": "application/json"
        }
        url = f"https://moskvichka.ru/api/articles?page={page}&limit={limit}"
        response = requests.get(url, headers=headers)

        print(f"🔄 Статус ответа: {response.status_code}")
        response.raise_for_status()
        data = response.json()

        items = data.get("items")
        if not items:
            print("⚠️ В ответе нет ключа 'items' или он пуст")
            return []

        print(f"✅ Найдено статей: {len(items)}")
        return items

    except requests.RequestException as e:
        print(f"❌ Ошибка HTTP: {e}")
    except ValueError as e:
        print(f"❌ Ошибка JSON: {e}")
    except Exception as e:
        print(f"❌ Неизвестная ошибка: {e}")

    return []


def format_article(article):
    title = article.get("title", "Без названия")
    slug = article.get("slug", "")
    date = article.get("published_at", "")[:10]
    excerpt = article.get("excerpt", "")
    url = f"https://moskvichka.ru/articles/{slug}"
    return f"📰 <b>{title}</b>\n📅 {date}\n\n{excerpt}\n\n🔗 {url}"


def check_new_articles():
    sent_ids = load_sent_articles()

    while True:
        print("\n🔎 Проверка сайта на новые статьи...\n")
        articles = fetch_articles()
        new_articles = []

        for art in articles:
            art_id = art.get("id")
            if art_id and art_id not in sent_ids:
                new_articles.append(art)
                sent_ids.add(art_id)

        for article in reversed(new_articles):  # от старой к новой
            msg = format_article(article)
            for chat_id in CHAT_IDS:
                bot.send_message(chat_id=chat_id, text=msg, parse_mode="HTML")

        print(f"✅ Новых статей отправлено: {len(new_articles)}")
        save_sent_articles(sent_ids)

        time.sleep(60)  # каждую 1 минуту


# Flask
app = Flask(__name__)


@app.route("/")
def home():
    return "Бот работает!"


if __name__ == "__main__":
    threading.Thread(target=check_new_articles, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
