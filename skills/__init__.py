"""
Пакет навыков голосового ассистента
"""

from skills.time_skills import TimeSkill, DateSkill
from skills.system_skills import ApplicationSkill, ScreenshotSkill, ClipboardSkill
from skills.web_skills import SearchSkill, YouTubeSkill
from skills.fun_skills import JokeSkill, WeatherSkill
from skills.game_skills import GameSkill

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
        GameSkill(),  # ⬅️ ДОБАВИЛИ ИГРОВОЙ НАВЫК
    ]

__all__ = [
    'TimeSkill', 'DateSkill', 'ApplicationSkill', 'ScreenshotSkill', 'ClipboardSkill',
    'SearchSkill', 'YouTubeSkill', 'JokeSkill', 'WeatherSkill', 'GameSkill', 'get_all_skills'
]