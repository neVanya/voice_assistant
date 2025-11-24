# Информационные навыки
from skills.time_skills import TimeSkill, DateSkill
from skills.info_skills import WeatherSkill, NewsSkill  # ⬅️ НОВАЯ ГРУППА

# Системные навыки
from skills.system_skills import ApplicationSkill, ScreenshotSkill, ClipboardSkill, ProcessSkill, SystemInfoSkill

# Веб-навыки
from skills.web_skills import SearchSkill, YouTubeSkill
from skills.wiki_skills import WikipediaSkill, RandomArticleSkill, DetailedArticleSkill

# Развлекательные навыки
from skills.fun_skills import JokeSkill  # ⬅️ ТОЛЬКО ШУТКИ

# Игровые навыки
from skills.game_skills import GameSkill

# Утилиты
from skills.reminder_skill import ReminderSkill


def get_all_skills():
    """Возвращает список всех навыков"""
    return [
        # Информационные
        TimeSkill(),
        DateSkill(),
        WeatherSkill(),
        NewsSkill(),

        # Системные
        ApplicationSkill(),
        ScreenshotSkill(),
        ClipboardSkill(),
        ProcessSkill(),
        SystemInfoSkill(),


        # Веб-навыки
        SearchSkill(),
        YouTubeSkill(),
        WikipediaSkill(),
        RandomArticleSkill(),
        DetailedArticleSkill(),

        # Развлекательные
        JokeSkill(),

        # Игровые
        GameSkill(),

        # Утилиты
        ReminderSkill(),
    ]


__all__ = [
    # Информационные
    'TimeSkill', 'DateSkill', 'WeatherSkill', 'NewsSkill',

    # Системные
    'ApplicationSkill', 'ScreenshotSkill', 'ClipboardSkill', 'ProcessSkill', 'SystemInfoSkill',

    # Веб-навыки
    'SearchSkill', 'YouTubeSkill', 'WikipediaSkill', 'RandomArticleSkill',

    # Развлекательные
    'JokeSkill',

    # Игровые
    'GameSkill',

    # Утилиты
    'ReminderSkill',

    'get_all_skills'
]