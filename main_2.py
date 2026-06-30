import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Ключевые слова для поиска
KEYWORDS = ['дизайн', 'фото', 'web', 'python']

# URL страницы со свежими статьями на Хабре
URL = 'https://habr.com/ru/all/'

def get_searchable_text(title, preview_text, tags):
    parts = []

    # Заголовок — участвует
    if title:
        parts.append(title.lower())
    if preview_text:
        text = preview_text.get_text(strip=True).lower()
        if text:
            parts.append(text)

    # Теги
    tag_text = ' '.join(
        tag.get_text(strip=True).lower() for tag in tags if tag.get_text(strip=True)
    )
    if tag_text:
        parts.append(tag_text)

    return ' '.join(parts)


def parse_habr_articles():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка при запросе к Хабру: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article', class_='tm-articles-list__item')

    matching_articles = []

    for article in articles:
        # Заголовок и ссылка
        title_tag = article.find('a', class_='tm-article-snippet__title-link')
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = 'https://habr.com' + title_tag['href']

        # Дата публикации
        time_tag = article.find('time')
        date_str = time_tag['datetime'] if time_tag else None
        date = 'Unknown'
        if date_str:
            try:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                date = date_obj.strftime('%Y-%m-%d')
            except Exception:
                date = 'Unknown'
        preview_block = article.find('div', class_='tm-article-snippet__body')
        # Теги
        tags = article.find_all('a', class_='tm-tags-list__link')

        search_text = get_searchable_text(title, preview_block, tags)

        # Проверка: есть ли хоть одно ключевое слово в объединённом тексте
        if any(kw.lower() in search_text for kw in KEYWORDS):
            matching_articles.append((date, title, link))

    # Вывод результатов
    if matching_articles:
        print("Найденные статьи по ключевым словам:")
        print('-' * 80)
        for date, title, link in matching_articles:
            print(f"{date} – {title} – {link}")
    else:
        print("Статьи с указанными ключевыми словами не найдены.")


if __name__ == "__main__":
    parse_habr_articles()