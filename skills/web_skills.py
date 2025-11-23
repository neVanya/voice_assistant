import webbrowser
from urllib.parse import quote
from skills.base_skill import BaseSkill


class SearchSkill(BaseSkill):
    """Навык поиска в интернете"""

    def __init__(self):
        super().__init__("Поиск")

    def get_keywords(self):
        return ["найди", "поищи", "ищи", "найти", "гугл", "поиск в интернете"]

    def execute(self, command: str, memory):
        # Извлекаем поисковый запрос
        query = self._extract_search_query(command)

        if query:
            url = f"https://www.google.com/search?q={quote(query)}"
            webbrowser.open(url)
            response = f"Ищу в Google: '{query}'. Открываю результаты поиска в браузере."
            return response
        else:
            response = "Что вы хотите найти в интернете?"
            return response

    def _extract_search_query(self, command: str) -> str:
        """Извлекает поисковый запрос из команды"""
        remove_words = ["найди", "поищи", "ищи", "найти", "в", "гугл", "google", "интернете"]
        words = command.split()
        filtered_words = [word for word in words if word.lower() not in remove_words]
        return ' '.join(filtered_words).strip()


class YouTubeSkill(BaseSkill):
    """Навык поиска на YouTube"""

    def __init__(self):
        super().__init__("YouTube")

    def get_keywords(self):
        return ["ютуб", "youtube", "видео", "найди на ютуб", "поищи видео"]

    def execute(self, command: str, memory):
        query = self._extract_search_query(command)

        if query:
            url = f"https://www.youtube.com/results?search_query={quote(query)}"
            webbrowser.open(url)
            response = f"Ищу на YouTube: '{query}'. Открываю результаты поиска."
            return response
        else:
            response = "Что вы хотите найти на YouTube?"
            return response

    def _extract_search_query(self, command: str) -> str:
        """Извлекает поисковый запрос из команды"""
        remove_words = ["найди", "поищи", "на", "ютуб", "youtube", "видео"]
        words = command.split()
        filtered_words = [word for word in words if word.lower() not in remove_words]
        return ' '.join(filtered_words).strip()