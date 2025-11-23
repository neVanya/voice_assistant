import feedparser
import random
from datetime import datetime
import logging

logger = logging.getLogger('VoiceAssistant')

# RSS-ленты из вашего кода
NEWS_FEEDS = {
    "lenta": "https://lenta.ru/rss/news",
    "kommersant": "https://www.kommersant.ru/RSS/news.xml",
    "rbc": "https://rssexport.rbc.ru/rbcnews/news/30/full.rss",
    "tass": "https://tass.ru/rss/v2.xml",
    "ria": "https://ria.ru/export/rss2/index.xml",
    "ivanovo_news": "https://ivgazeta.ru/rss",
    "ivanovo_region": "https://www.ivanovonews.ru/rss.xml",
    "ivanovo_today": "https://ivgorod.ru/rss"
}


class NewsService:
    """Сервис для получения новостей"""

    def get_news(self, category="general", limit=3):
        """Получает свежие новости из RSS-лент"""
        try:
            # Выбираем подходящую RSS-ленту
            feed_url = NEWS_FEEDS["lenta"]  # по умолчанию Lenta.ru

            if category in ["technology", "tech"]:
                feed_url = "https://habr.com/ru/rss/articles/"
            elif category in ["politics", "pol"]:
                feed_url = NEWS_FEEDS["ria"]
            elif category in ["economics", "eco"]:
                feed_url = NEWS_FEEDS["rbc"]
            elif category in ['ivanovo']:
                feed_url = NEWS_FEEDS["ivanovo_news"]

            # Парсим RSS
            feed = feedparser.parse(feed_url)

            if not feed.entries:
                return "Не удалось загрузить новости"

            # Формируем список новостей
            news_items = []
            for entry in feed.entries[:limit]:
                title = self._clean_html_tags(entry.title)
                news_items.append(title)

            return news_items

        except Exception as e:
            logger.error(f"Ошибка получения новостей: {e}")
            return f"Ошибка при получении новостей: {e}"

    def _clean_html_tags(self, text):
        """Очищает текст от HTML-тегов"""
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)

    def read_news_headlines(self, category="general", count=3):
        """Читает заголовки новостей вслух"""
        news = self.get_news(category, count)

        if isinstance(news, str):  # Если вернулась ошибка
            return news

        if not news:
            return "Новости не найдены"

        # Формируем текст для озвучивания
        if len(news) == 1:
            speech_text = f"Главная новость: {news[0]}"
        else:
            speech_text = f"Вот последние {len(news)} новостей: " + ". ".join(news)

        return speech_text


# Глобальный экземпляр сервиса новостей
news_service = NewsService()