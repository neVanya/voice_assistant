import random
from core.plugin_base import BasePlugin


class JokePlugin(BasePlugin):
    """Плагин шуток с расширенными возможностями"""

    def __init__(self):
        super().__init__("Шутки", "2.0")
        self.jokes_by_category = {
            "программирование": [
                "Почему программисты путают Хэллоуин и Рождество? Потому что Oct 31 == Dec 25!",
                "Сколько программистов нужно, чтобы вкрутить лампочку? Ни одного, это hardware проблема!",
            ],
            "математика": [
                "Почему математик не мог спать? Он считал овец в комплексной плоскости!",
                "Что сказал один вектор другому? Я тебя в проекции жду!",
            ],
            "общие": [
                "Что сказал один байт другому? Я тебя в цикле жду!",
                "Почему компьютер пошел к врачу? У него был вирус!",
            ]
        }

    def get_commands(self) -> list:
        return [
            "расскажи шутку",
            "пошути",
            "рассмеши",
            "шутка про",
            "анекдот"
        ]

    def execute(self, command: str, memory, **kwargs) -> str:
        command_lower = command.lower()

        # Определяем категорию
        category = "общие"
        for cat in self.jokes_by_category.keys():
            if cat in command_lower:
                category = cat
                break

        jokes = self.jokes_by_category.get(category, self.jokes_by_category["общие"])
        return random.choice(jokes)