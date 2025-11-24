import wikipedia
import re
import logging
from skills.base_skill import BaseSkill

logger = logging.getLogger('VoiceAssistant')


class WikipediaSkill(BaseSkill):
    """Навык поиска в Википедии"""

    def __init__(self):
        super().__init__("Википедия")
        wikipedia.set_lang("ru")

    def get_keywords(self):
        return [
            "найди в википедии", "википедия", "найди про", "что такое",
            "кто такой", "кто такая", "расскажи про", "найди информацию о",
            "что значит", "определение", "расскажи о", "кто такой был"
        ]

    def execute(self, command: str, memory):
        try:
            # Очищаем запрос от ключевых слов
            clean_query = self._clean_query(command)

            if not clean_query:
                return "Пожалуйста, уточните, что вы хотите найти в Википедии."

            # Ищем страницы
            search_results = wikipedia.search(clean_query)
            if not search_results:
                return f"По запросу '{clean_query}' ничего не найдено в Википедии."

            # Берем первую найденную страницу
            page_title = search_results[0]

            # Получаем краткое содержание
            summary = wikipedia.summary(page_title, sentences=2)

            # Очищаем текст
            summary = self._clean_text(summary)

            response = f"Вот что я нашел о '{page_title}': {summary}"
            return response

        except wikipedia.exceptions.DisambiguationError as e:
            # Если запрос неоднозначный
            options = e.options[:3]
            options_str = ", ".join(options)
            return f"Уточните запрос. Возможно, вы имели в виду: {options_str}"

        except wikipedia.exceptions.PageError:
            return f"Страница '{clean_query}' не найдена. Попробуйте другой запрос."

        except Exception as e:
            logger.error(f"Ошибка поиска в Википедии: {e}")
            return f"Произошла ошибка при поиске: {str(e)}"

    def _clean_query(self, query: str) -> str:
        """Очищает запрос от ключевых слов"""
        keywords = [
            "найди в википедии", "википедия", "найди про", "что такое",
            "кто такой", "кто такая", "расскажи про", "найди информацию о",
            "что значит", "определение", "расскажи о", "кто такой был"
        ]

        clean_query = query.lower()
        for keyword in keywords:
            clean_query = clean_query.replace(keyword, "")

        return clean_query.strip()

    def _clean_text(self, text: str) -> str:
        """Очищает текст от HTML-тегов и лишних символов"""
        # Удаляем HTML-теги
        text = re.sub(r'<[^>]+>', '', text)
        # Удаляем текст в скобках
        text = re.sub(r'\([^)]*\)', '', text)
        # Убираем лишние пробелы
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


class RandomArticleSkill(BaseSkill):
    """Навык случайных статей из Википедии"""

    def __init__(self):
        super().__init__("Случайная статья")
        wikipedia.set_lang("ru")

    def get_keywords(self):
        return [
            "случайная статья", "рандомная статья", "что-нибудь интересное",
            "расскажи что-то новое", "интересный факт"
        ]

    def execute(self, command: str, memory):
        try:
            random_title = wikipedia.random()
            summary = wikipedia.summary(random_title, sentences=1)

            summary = self._clean_text(summary)

            response = f"Случайная статья: '{random_title}'. {summary}"
            return response

        except Exception as e:
            logger.error(f"Ошибка получения случайной статьи: {e}")
            return "Не удалось получить случайную статью. Попробуйте еще раз."

    def _clean_text(self, text: str) -> str:
        """Очищает текст от HTML-тегов и лишних символов"""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\([^)]*\)', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()