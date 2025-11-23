import random
from skills.base_skill import BaseSkill
from utils.weather_service import weather_service


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


class WeatherSkill(BaseSkill):
    """Навык получения реальной погоды"""

    def __init__(self):
        super().__init__("Погода")

    def get_keywords(self):
        return [
            "погода", "погоду", "температура", "градус",
            "какая погода", "погода в", "температура в", "прогноз погоды"
        ]

    def execute(self, command: str, memory):
        # Определяем город из команды
        city = weather_service.get_city_from_text(command)

        # Проверяем, не запрошен ли прогноз
        if 'прогноз' in command or 'завтра' in command:
            # Упрощенный прогноз - используем текущую погоду
            current_weather = weather_service.get_weather(city)
            if "Ошибка" in current_weather:
                return current_weather

            if 'завтра' in command:
                return f"Сейчас: {current_weather}. На завтра ожидается похожая погода."
            else:
                return f"Прогноз на сегодня: {current_weather}"
        else:
            # Текущая погода
            return weather_service.get_weather(city)