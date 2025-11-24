import random
from skills.base_skill import BaseSkill


class JokeSkill(BaseSkill):
    """Навык рассказывания шуток"""

    def __init__(self):
        super().__init__("Шутки")

    def get_keywords(self):
        return ["расскажи шутку", "шутка", "пошути", "рассмеши"]

    def execute(self, command: str, memory):
        jokes = [
            "Почему программисты путают Хэллоуин и Рождество? Потому что Oct 31 равно Dec 25!",
            "Как называется юмор айтишников? Чёрный ящик!",
            "Почему Python стал таким популярным? Потому что его змеиный характер всех завораживает!",
            "Сколько программистов нужно, чтобы вкрутить лампочку? Ни одного, это hardware проблема!",
            "Что сказал один байт другому? Я тебя в цикле жду!"
        ]

        response = random.choice(jokes)
        return response

