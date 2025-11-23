import json
import os
from datetime import datetime
from config.settings import Settings


class MemoryManager:
    """Управление памятью ассистента с сохранением в файл"""

    def __init__(self):
        self.memory_file = os.path.join(Settings.DATA_PATH, "memory.json")
        self.data = self._load_memory()
        self.tts_engine = None  # Добавляем ссылку на TTS движок

    def _load_memory(self) -> dict:
        """Загружает память из файла"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки памяти: {e}")

        # Память по умолчанию
        return {
            "user_name": None,
            "conversation_history": [],
            "preferences": {},
            "created_at": datetime.now().isoformat()
        }

    def _save_memory(self):
        """Сохраняет память в файл"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения памяти: {e}")

    def remember_name(self, name: str) -> str:
        """Запоминает имя пользователя (БЕЗ озвучивания)"""
        self.data["user_name"] = name
        self._save_memory()
        response = f"Приятно познакомиться, {name}! Запомнил ваше имя."

        # ⚠️ УБИРАЕМ озвучивание отсюда - будет в assistant_core.py
        # if self.tts_engine:
        #     self.tts_engine.speak(response)

        return response

    @property
    def user_name(self):
        return self.data.get("user_name")

    def get_personalized_response(self, response: str) -> str:
        """Добавляет имя пользователя в ответ если известно"""
        if self.user_name:
            return f"{self.user_name}, {response}"
        return response

    def add_to_history(self, user_text: str, assistant_text: str):
        """Добавляет разговор в историю"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_text,
            "assistant": assistant_text
        }
        self.data["conversation_history"].append(entry)

        # Ограничиваем историю 100 записями
        if len(self.data["conversation_history"]) > 100:
            self.data["conversation_history"] = self.data["conversation_history"][-100:]

        self._save_memory()

    def get_recent_history(self, count: int = 5) -> list:
        """Возвращает последние записи истории"""
        return self.data["conversation_history"][-count:]