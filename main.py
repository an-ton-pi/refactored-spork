import os
import time
import threading
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from flask import Flask

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_IDS = os.getenv('CHAT_IDS', '').split(',')

bot = Bot(token=TELEGRAM_TOKEN)
last_sent_links = set()

def get_articles():
    url = 'https://moskvichka.ru/articles'
    response = requests.get(url)
    print("DEBUG: первые 1000 символов страницы:")
    print(response.text[:1000])  # Выводим в лог первые 1000 символов HTML для анализа

    soup = BeautifulSoup(response.text, 'html.parser')

    articles = []
    for item in soup.select('a.article-card'):
        title = item.select_one('.article-card__title')
        if title and item.get('href'):
            link = item['href']
            full_link = f"https://moskvichka.ru{link}"
            articles.append({
                'title': title.text.strip(),
                'url': full_link
            })
    return articles

def check_articles_loop():
    print("🔄 check_articles_loop запущен")
    global last_sent_links

    while True:
        try:
            print("🔎 Проверка сайта на новые статьи...")
            articles = get_articles()
            print(f"👀 Найдено статей: {len(articles)}")

            for art in articles:
                print(f"📄 {art['title']} — {art['url']}")

            new_articles = [a for a in articles if a['url'] not in last_sent_links]

            for article in new_articles:
                message = f"📰 <b>{article['title']}</b>\n{article['url']}"
                for chat_id in CHAT_IDS:
                    try:
                        bot.send_message(chat_id=chat_id.strip(), text=message, parse_mode="HTML")
                        print(f"✅ Отправлено в чат {chat_id}: {article['title']}")
                    except Exception as send_error:
                        print(f"❌ Ошибка при отправке в чат {chat_id}: {send_error}")
                last_sent_links.add(article['url'])

            print(f"✅ Новых статей отправлено: {len(new_articles)}")

        except Exception as e:
            print("🔥 Ошибка при проверке статей:", e)

        time.sleep(60)  # ждать 1 минуту

# Запускаем проверку статей в отдельном потоке
threading.Thread(target=check_articles_loop, daemon=True).start()

@app.route('/')
def index():
    return "✅ Бот работает"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
