import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Оптимизированные настройки голосового ассистента"""

    # Голосовые настройки
    VOICE_RATE = 220  # ⬅️ Увеличили скорость речи
    VOICE_VOLUME = 1.0
    VOICE_PITCH_SHIFT = 8

    # Оптимизированные настройки распознавания
    SPEECH_TIMEOUT = 3  # ⬅️ Уменьшили время ожидания
    PHRASE_TIME_LIMIT = 4  # ⬅️ Уменьшили лимит фразы

    # Ключевые слова активации
    WAKE_WORDS = ["ассистент", "помощник", "джарвис", "окей", "привет"]

    # API ключи
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '1da0ee3f66e9121f7926c78c491e4569')

    # Пути
    DATA_PATH = "data"
    CACHE_PATH = "data/cache"

    @classmethod
    def setup_directories(cls):
        """Создает необходимые директории"""
        os.makedirs(cls.DATA_PATH, exist_ok=True)
        os.makedirs(cls.CACHE_PATH, exist_ok=True)


# Инициализация при импорте
Settings.setup_directories()