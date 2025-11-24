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

            # УВЕЛИЧИВАЕМ КОЛИЧЕСТВО ПРЕДЛОЖЕНИЙ ДО 4-5
            summary = wikipedia.summary(page_title, sentences=5)

            # Очищаем текст
            summary = self._clean_text(summary)

            # Форматируем ответ для лучшей читаемости
            response = f"📚 Вот что я нашел о '{page_title}':\n\n{summary}"
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
        # Удаляем текст в скобках (но оставляем основные)
        text = re.sub(r'\[.*?\]', '', text)  # удаляем квадратные скобки
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
            "расскажи что-то новое", "интересный факт", "удиви меня",
            "что почитать", "открой что-то новое"
        ]

    def execute(self, command: str, memory):
        try:
            random_title = wikipedia.random()
            # УВЕЛИЧИВАЕМ ДО 3-4 ПРЕДЛОЖЕНИЙ ДЛЯ СЛУЧАЙНЫХ СТАТЕЙ
            summary = wikipedia.summary(random_title, sentences=4)

            summary = self._clean_text(summary)

            # Более информативный формат ответа
            response = f"🔍 Случайная статья: '{random_title}'\n\n{summary}"
            return response

        except Exception as e:
            logger.error(f"Ошибка получения случайной статьи: {e}")
            return "Не удалось получить случайную статью. Попробуйте еще раз."

    def _clean_text(self, text: str) -> str:
        """Очищает текст от HTML-тегов и лишних символов"""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


class DetailedArticleSkill(BaseSkill):
    """Навык для получения подробных статей"""

    def __init__(self):
        super().__init__("Подробная статья")
        wikipedia.set_lang("ru")

    def get_keywords(self):
        return [
            "подробно о", "расскажи подробнее", "детальная информация",
            "полная статья", "больше информации о", "развернутый ответ"
        ]

    def execute(self, command: str, memory):
        try:
            # Очищаем запрос
            clean_query = self._extract_query(command)

            if not clean_query:
                return "О ком или о чем вы хотите получить подробную информацию?"

            # Ищем страницу
            search_results = wikipedia.search(clean_query)
            if not search_results:
                return f"По запросу '{clean_query}' ничего не найдено."

            page_title = search_results[0]

            # ПОЛУЧАЕМ ПОЛНУЮ СТАТЬЮ ИЛИ ОЧЕНЬ ДЛИННОЕ ОПИСАНИЕ
            try:
                # Пробуем получить полную страницу
                page = wikipedia.page(page_title)
                content = page.content

                # Берем первые 800 символов (примерно 6-8 предложений)
                if len(content) > 800:
                    summary = content[:800] + "..."
                else:
                    summary = content

            except:
                # Если не получилось, берем длинное описание
                summary = wikipedia.summary(page_title, sentences=8)

            summary = self._clean_text(summary)

            response = f"📖 Подробная информация о '{page_title}':\n\n{summary}"
            return response

        except Exception as e:
            logger.error(f"Ошибка получения подробной статьи: {e}")
            return "Не удалось получить подробную информацию. Попробуйте другой запрос."

    def _extract_query(self, command: str) -> str:
        """Извлекает запрос из команды"""
        keywords = ["подробно о", "расскажи подробнее", "детальная информация",
                    "полная статья", "больше информации о", "развернутый ответ"]

        clean_query = command.lower()
        for keyword in keywords:
            clean_query = clean_query.replace(keyword, "")

        return clean_query.strip()

    def _clean_text(self, text: str) -> str:
        """Очищает текст"""
        text = re.sub(r'==.*?==', '', text)  # удаляем заголовки
        text = re.sub(r'\[.*?\]', '', text)  # удаляем ссылки
        text = re.sub(r'\s+', ' ', text)
        return text.strip()