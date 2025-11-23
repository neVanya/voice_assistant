from abc import ABC, abstractmethod
import logging

logger = logging.getLogger('VoiceAssistant')


class BaseSkill(ABC):
    """Абстрактный базовый класс для всех навыков ассистента"""

    def __init__(self, name: str):
        self.name = name
        self.logger = logger

    @abstractmethod
    def get_keywords(self) -> list:
        """Возвращает ключевые слова для активации навыка"""
        pass

    @abstractmethod
    def execute(self, command: str, memory) -> str:
        """Выполняет команду и возвращает ответ"""
        pass

    def match(self, text: str) -> bool:
        """Проверяет, подходит ли текст для этого навыка"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.get_keywords())

    def get_description(self) -> str:
        """Возвращает описание навыка для справки"""
        keywords = self.get_keywords()
        return f"{self.name}: {', '.join(keywords[:3])}{'...' if len(keywords) > 3 else ''}"

    def speak_response(self, text: str, tts_engine):
        """Озвучивает ответ и логирует его"""
        self.logger.info(f"Навык {self.name}: {text}")

        # Если tts_engine доступен - озвучиваем, иначе просто выводим
        if tts_engine and hasattr(tts_engine, 'speak'):
            tts_engine.speak(text)
        else:
            print(f"🔊 {text}")  # Вывод в консоль для тестов

        return text