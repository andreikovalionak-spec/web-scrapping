import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime
import time
import random

''' Настройки'''
KEYWORDS = ['дизайн', 'фото', 'web', 'python']
RSS_URL = "https://habr.com/ru/rss/all/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
}


def check_keywords(text):
    if not text:
        return False
    text_lower = text.lower()
    return any(kw in text_lower for kw in KEYWORDS)


def get_full_article_text(url):
    """Скачивает статью и извлекает основной текст"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        ''' Основной текст статьи в блоке с классом 'article-formatted-body'''
        content_block = soup.find('div', class_='article-formatted-body')
        if not content_block:
            return None

        ''' Извлекаем весь текст из блока'''
        text = content_block.get_text(separator=' ', strip=True)
        return text

    except Exception as e:
        print(f"Ошибка при загрузке {url}: {e}")
        return None


def main():
    print(f"Анализ  текста статей по ключевым словам: {KEYWORDS}")

    feed = feedparser.parse(RSS_URL)
    if feed.bozo:
        print("Не удалось получить RSS ленту.")
        return

    found_articles = []

    for entry in feed.entries[:10]:
        title = entry.title
        link = entry.link
        published = entry.get('published_parsed')
        date_str = datetime(*published[:6]).strftime("%Y-%m-%d") if published else "Unknown"

        print(f"Проверяю: {title}...")

        ''' Сначала проверяем preview '''
        desc = entry.get('summary', '')
        if check_keywords(title) or check_keywords(desc):
            ''' Если совпало в preview, проверяем полный текст'''
            full_text = get_full_article_text(link)

            if full_text and check_keywords(full_text):
                found_articles.append((date_str, title, link))
                print(f"  ПОДХОДИТ!")
            else:
                print(f"  Не подходит")
        else:
            print(f" Нет совпадений в preview.")
        time.sleep(random.uniform(1, 3))

    print("\n" + "=" * 50)
    print("РЕЗУЛЬТАТЫ : ")
    for date_str, title, link in found_articles:
        print(f"{date_str} – {title} – {link}")
    print("=" * 50)


if __name__ == "__main__":
    main()