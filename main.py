import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

# Определяем список ключевых слов
KEYWORDS = ['дизайн', 'фото', 'web', 'python']

# URL страницы со свежими статьями на Хабре
URL = 'https://habr.com/ru/all/'

def parse_habr_articles():
    try:
        # Отправляем GET‑запрос к странице
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(URL, headers=headers)
        response.raise_for_status()  # Проверяем статус ответа

        # Парсим HTML‑код страницы
        soup = BeautifulSoup(response.text, 'html.parser')

        # Находим все статьи на странице (ищем карточки статей)
        articles = soup.find_all('article', class_='tm-articles-list__item')

        matching_articles = []

        for article in articles:
            # Извлекаем заголовок и ссылку
            title_tag = article.find('a', class_='tm-article-snippet__title-link')
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = 'https://habr.com' + title_tag['href']

            # Извлекаем дату публикации
            time_tag = article.find('time')
            date_str = time_tag['datetime'] if time_tag else 'Unknown'
            # Преобразуем дату в читаемый формат
            try:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                date = date_obj.strftime('%Y-%m-%d')
            except:
                date = 'Unknown'

            preview_texts = []

            # Текст описания статьи
            text_block = article.find('div', class_='article-formatted-body')
            if text_block:
                preview_texts.append(text_block.get_text(strip=True))

            # Теги статьи
            tags = article.find_all('a', class_='tm-tags-list__link')
            tag_text = ' '.join([tag.get_text(strip=True) for tag in tags])
            if tag_text:
                preview_texts.append(tag_text)

            # Объединяем все preview‑данные в один текст для поиска
            full_preview_text = ' '.join(preview_texts).lower()

            # Проверяем, есть ли хотя бы одно ключевое слово в preview‑тексте
            if any(keyword.lower() in full_preview_text for keyword in KEYWORDS):
                matching_articles.append((date, title, link))

        # Выводим результаты в консоль
        if matching_articles:
            print("Найденные статьи по ключевым словам:")
            print("-!" * 80)
        for date, title, link in matching_articles:
                print(f"{date} – {title} – {link}")
        else:
            print("Статьи с указанными ключевыми словами не найдены.")

    except requests.RequestException as e:
        print(f"Ошибка при запросе к Хабру: {e}")
    except Exception as e:
        print(f"Произошла ошибка при парсинге: {e}")

if __name__ == "__main__":
    parse_habr_articles()