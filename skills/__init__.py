"""
Пакет навыков голосового ассистента
"""

from skills.time_skills import TimeSkill, DateSkill
from skills.system_skills import ApplicationSkill, ScreenshotSkill, ClipboardSkill
from skills.web_skills import SearchSkill, YouTubeSkill
from skills.fun_skills import JokeSkill, WeatherSkill
from skills.game_skills import GameSkill
from skills.wiki_skills import WikipediaSkill, RandomArticleSkill  # ⬅️ ДОБАВИЛИ ВИКИПЕДИЮ

def get_all_skills():
    """Возвращает список всех навыков"""
    return [
        TimeSkill(),
        DateSkill(),
        ApplicationSkill(),
        ScreenshotSkill(),
        ClipboardSkill(),
        SearchSkill(),
        YouTubeSkill(),
        JokeSkill(),
        WeatherSkill(),
        GameSkill(),
        WikipediaSkill(),      # ⬅️ ДОБАВИЛИ
        RandomArticleSkill(),  # ⬅️ ДОБАВИЛИ
    ]

__all__ = [
    'TimeSkill', 'DateSkill', 'ApplicationSkill', 'ScreenshotSkill', 'ClipboardSkill',
    'SearchSkill', 'YouTubeSkill', 'JokeSkill', 'WeatherSkill', 'GameSkill',
    'WikipediaSkill', 'RandomArticleSkill', 'get_all_skills'  # ⬅️ ОБНОВИЛИ
]