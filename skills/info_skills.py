from skills.base_skill import BaseSkill
from utils.weather_service import weather_service
from skills.time_skills import TimeSkill, DateSkill


class WeatherSkill(BaseSkill):
    """Навык получения информации о погоде"""

    def __init__(self):
        super().__init__("Погода")

    def get_keywords(self):
        return [
            "погода", "погоду", "температура", "градус",
            "какая погода", "погода в", "температура в", "прогноз погоды"
        ]

    def execute(self, command: str, memory):
        city = weather_service.get_city_from_text(command)

        if 'прогноз' in command or 'завтра' in command:
            current_weather = weather_service.get_weather(city)
            if "Ошибка" in current_weather:
                return current_weather
            if 'завтра' in command:
                return f"Сейчас: {current_weather}. На завтра ожидается похожая погода."
            else:
                return f"Прогноз на сегодня: {current_weather}"
        else:
            return weather_service.get_weather(city)


class NewsSkill(BaseSkill):
    """Навык получения новостей"""

    def __init__(self):
        super().__init__("Новости")

    def get_keywords(self):
        return [
            "новости", "что нового", "свежие новости", "последние новости",
            "новости технологии", "новости политики", "городские новости"
        ]

    def execute(self, command: str, memory):
        from utils.news_service import news_service

        categories = {
            "технологии": "technology",
            "политика": "politics",
            "экономика": "economics",
            "город": "ivanovo"
        }

        category = "general"
        for cat_ru, cat_en in categories.items():
            if cat_ru in command:
                category = cat_en
                break

        return news_service.read_news_headlines(category, 3)