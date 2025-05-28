import requests
from bs4 import BeautifulSoup

# URL страницы со статьями
url = 'https://moskvichka.ru/articles'

# Заголовки для запроса (можно добавить, если сайт требует)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

# Выполняем GET-запрос к странице
response = requests.get(url, headers=headers)

# Проверяем успешность запроса
if response.status_code == 200:
    # Создаём объект BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Ищем все элементы статей (предположим, что статьи находятся в тегах <a> с классом 'card-article')
    articles = soup.find_all('a', class_='card-article')

    # Проверяем, найдены ли статьи
    if articles:
        print(f'Найдено статей: {len(articles)}\n')

        # Проходим по каждой найденной статье
        for article in articles:
            # Извлекаем заголовок статьи
            title = article.get_text(strip=True)

            # Извлекаем ссылку на статью
            link = article.get('href')

            # Если ссылка относительная, добавляем домен
            if link and not link.startswith('http'):
                link = f'https://moskvichka.ru{link}'

            # Выводим информацию о статье
            print(f'Заголовок: {title}')
            print(f'Ссылка: {link}\n')
    else:
        print('Статьи не найдены. Возможно, структура сайта изменилась.')
else:
    print(f'Ошибка при запросе страницы: {response.status_code}')
